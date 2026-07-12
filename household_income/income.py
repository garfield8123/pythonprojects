from datetime import datetime
import pdfplumber

def contains_county(data):
    return (
        bool(data) and
        bool(data[0]) and
        isinstance(data[0][0], str) and
        "county" in data[0][0].lower()
    )

import pdfplumber

def incomedata(data, numofhouseholds):
    fullincomedict = {}
    
    # Target column calculation: 
    # Col 0: County name, Col 1: Income category text, Col 2: 1-person household, etc.
    target_column = 1 + int(numofhouseholds)

    with pdfplumber.open(data) as pdf:
        for p in pdf.pages:
            tables = p.extract_tables()
            if not tables:
                continue
                
            for t in tables:
                if len(t) <= 4:
                    continue
                
                current_county = None
                
                for r in t:
                    # Guardrail: Ignore rows that don't have enough columns (avoids IndexError)
                    if len(r) <= target_column or r[1] is None:
                        continue
                    
                    # Track and update the current county name cleanly
                    # Row 0 of a section usually has the county name in r[0]
                    if r[0] and "county" not in r[0].lower() and "income" not in r[0].lower():
                        current_county = r[0].split("\n")[0].strip()
                    
                    # If we don't have a valid county context yet, skip row processing
                    if not current_county:
                        continue

                    # Clean the data strings
                    category_name = r[1].replace("\n", " ").strip()
                    income_value = r[target_column].replace("\n", " ").strip() if r[target_column] else "N/A"
                    
                    # Build out the nested dictionary structures safely
                    if current_county not in fullincomedict:
                        fullincomedict[current_county] = {}
                        
                    fullincomedict[current_county].update({category_name: income_value})
    return fullincomedict
    
import requests

def downloadpdf(website, filename):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(website, headers=headers)

    # Check if it's actually a PDF
    if "application/pdf" not in r.headers.get("Content-Type", ""):
    #    print("❌ Not a PDF. Got:", r.headers.get("Content-Type"))
    #    print(r.text[:300])  # Debug output
        return

    with open(filename, "wb") as f:
        f.write(r.content)

    #print("✅ PDF downloaded successfully")


def getincomekeys(numofhousehold, county):
    year=str(datetime.now().year)
    downloadpdf("https://www.hcd.ca.gov/sites/default/files/docs/grants-and-funding/income-limits-%s.pdf" %year, "income-limits-%s.pdf" %year)
    incomedict = incomedata("income-limits-%s.pdf" %year, int(numofhousehold))
    print("here")
    return incomedict.keys()

def getincomedata(numofhousehold, county):
    year=str(datetime.now().year)
    downloadpdf("https://www.hcd.ca.gov/sites/default/files/docs/grants-and-funding/income-limits-%s.pdf" %year, "income-limits-%s.pdf" %year)
    incomedict = incomedata("income-limits-%s.pdf" %year, int(numofhousehold))
    return incomedict.get(county)


#https://www.hcd.ca.gov/sites/default/files/docs/grants-and-funding/income-limits-2025.pdf

if __name__ == "__main__":
    print("Alameda County: ", getincomedata(1,"Alameda County"))
    print("San Francisco County: ", getincomedata(1,"San Francisco County"))
    print("Santa Clara County: ", getincomedata(1,"Santa Clara County"))
    print("San Mateo County: ", getincomedata(1,"San Mateo County"))
    print("Contra Costa County: ", getincomedata(1,"Contra Costa County"))
