import csv
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path



def loadwebsite(city_key, discord=None):
    print(discord)
    project_dir = Path.cwd()
    if discord is not None:
        project_dir="housefind/"
    with open(project_dir + "redfincity.json", "r") as file:
        CALIFORNIA_CITIES = json.load(file)
    city_path = CALIFORNIA_CITIES.get(city_key.lower())
    if not city_path:
        raise ValueError(f"City '{city_key}' is not mapped. Please find its URL block on Redfin and add it to CALIFORNIA_CITIES.")
        
    site = f"https://www.redfin.com/city/{city_path}/filter/sort=lo-price,property-type=house+condo+townhouse"
    print(f"Scraping URL: {site}")

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    parsed_json_data = []
    try:
        driver.get(site)
        page = BeautifulSoup(driver.page_source, features='html.parser')
        script_tags = page.find_all('script', type="application/ld+json")
        
        for tag in script_tags:
            if tag.string:
                try:
                    parsed_json_data.append(json.loads(tag.string))
                except json.JSONDecodeError:
                    continue
    finally:
        driver.quit()
        
    return parsed_json_data

def save_to_csv(extracted_blocks, filename):
    print('save1')
    properties_list = []
    for block in extracted_blocks:
        items = block if isinstance(block, list) else [block]
        
        # Added 'Beds' and 'Baths' to our temporary collection bucket
        temp_data = {"Address": "", "URL": "", "Price": "", "Beds": "", "Baths": ""}
        
        for item in items:
            if not isinstance(item, dict):
                continue
            
            if item.get("@type") in ["SingleFamilyResidence", "House", "Condominium", "Townhouse"]:
                addr_obj = item.get("address", {})
                if isinstance(addr_obj, dict):
                    temp_data["Address"] = f"{addr_obj.get('streetAddress', '')}, {addr_obj.get('addressLocality', '')}, {addr_obj.get('addressRegion', '')} {addr_obj.get('postalCode', '')}".strip(", ")
                if item.get("url"):
                    temp_data["URL"] = item.get("url")
                
                # --- Extract Beds & Baths dynamically ---
                # Redfin schemas sometimes use 'numberOfBedrooms' or fallback to 'numberOfRooms'
                beds = item.get("numberOfBedrooms") or item.get("numberOfRooms")
                baths = item.get("numberOfBathroomsTotal") or item.get("numberOfBathrooms")
                
                if beds:
                    temp_data["Beds"] = beds
                if baths:
                    temp_data["Baths"] = baths
                    
            elif item.get("@type") == "Product":
                offers = item.get("offers", {})
                if isinstance(offers, dict):
                    temp_data["Price"] = offers.get("price", "")
                if item.get("url"):
                    temp_data["URL"] = item.get("url")
        
        # Verify we captured some form of data before keeping the row
        if temp_data["Address"] or temp_data["Price"] or temp_data["URL"]:
            properties_list.append(temp_data)

    if properties_list:
        print(filename)
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            # Added "Beds" and "Baths" to the CSV Header mapping list
            fieldnames = ["Address", "URL", "Price", "Beds", "Baths"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            writer.writeheader()
            for prop in properties_list:
                writer.writerow(prop)
        print(f"Successfully saved {len(properties_list)} records to '{filename}'.\n")
        #return temp_data
    else:
        print("No valid properties found matching the expected schema layout.\n")
    print('save2')
    return properties_list
    #return temp_data

def getaverageprice(properties, bedroom):
    one_bed_prices = []
    one_bed_properties = []
    
    for prop in properties:
        price_str = prop.get("Price")
        beds_str = prop.get("Beds")
        
        if price_str and beds_str:
            try:
                # Sanitize price: Strip out standard Redfin formatting symbols ($, commas)
                clean_price = str(price_str).replace("$", "").replace(",", "").strip()
                price = float(clean_price)
                
                # Sanitize beds
                beds = int(float(str(beds_str).strip()))
                
                # Check match against target bedroom count
                if beds == bedroom:
                    one_bed_prices.append(price)
                    one_bed_properties.append({
                        "Address": prop.get("Address"),
                        "Price": price, 
                        "URL": prop.get("URL")
                    })
            except ValueError:
                continue

    if not one_bed_prices:
        return f"❌ No {bedroom}-bedroom properties found matching that criteria in the active dataset."

    # Calculate average
    avg_price = sum(one_bed_prices) / len(one_bed_prices)
    
    # Build propertystring efficiently
    propertystring_lines = []
    for idx, item in enumerate(one_bed_properties, 1):
        propertystring_lines.append(f"{idx}. {item['Address']} -> ${item['Price']:,.2f} -> {item['URL']}")
    
    propertystring = "\n".join(propertystring_lines)
    
    # Combined output message
    final_output = f"📊 **Average Price for {bedroom} Bed(s):** ${avg_price:,.2f}\n\n{propertystring}"
    
    # Discord text limit fallback guardrail (max 2000 chars)
    if len(final_output) > 2000:
        return f"📊 **Average Price for {bedroom} Bed(s):** ${avg_price:,.2f}\n\n⚠️ *List truncated due to Discord character limits.*"
        
    return final_output

def findcityInfo(target_city, bedroom, discord=None):
    print("here")
    if discord is not None:
        print("here3")
        raw_data = loadwebsite(target_city, discord)
    else:
        raw_data = loadwebsite(target_city)
    output_file="redfin_properties.csv"
    print("here2")
    properties_list=save_to_csv(raw_data, output_file)
    print(properties_list)
    propertystring = getaverageprice(properties_list, int(bedroom))
    return propertystring

def redfincityjson(CityUpdate=None, discord=None):
    if CityUpdate is not None:
        project_dir = Path.cwd()
        if discord is not None:
            project_dir="housefind/"
        with open(project_dir + "redfincity.json", "r") as file:
            CALIFORNIA_CITIES = json.load(file)
        CALIFORNIA_CITIES.update(CityUpdate)
        with open(project_dir + "redfincity.json", "w") as file:
            json.dump(CALIFORNIA_CITIES, file, indent=4)
    else:
        project_dir = Path.cwd()
        if discord is not None:
            project_dir="housefind/"
        with open(project_dir + "redfincity.json", "r") as file:
            CALIFORNIA_CITIES = json.load(file)
        return ' '.join(CALIFORNIA_CITIES.keys())

if __name__ == "__main__":
    # --- Execute Script For Any City ---
    target_city = "walnut_creek" 
    output_file = f"redfin_{target_city}_properties.csv"

    #getaverageprice(target_city, 1)
    raw_data = loadwebsite(target_city)
    #print(raw_data)
    properties_list=save_to_csv(raw_data, output_file)
    propertystring =getaverageprice(properties_list, 1)
    #print(avg_price)
    print(propertystring)
    #print(temp_data)
