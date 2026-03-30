from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import 
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def loadwebsite(site, ciphertext):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    driver.get(site)

    # Type in ciphertext
    ciphertextelement = driver.find_element(By.ID,'cipher_identifier_ciphertext')
    ciphertextelement.send_keys(ciphertext)
    #print("Typed text:", ciphertextelement.get_attribute('value'))

    # Click the Analyze button
    analyzelement = driver.find_element(By.CSS_SELECTOR, '[data-post="ciphertext,clues"]')
    analyzelement.click()

    # Wait for the results div to appear (up to 10 seconds)
    try:
        result_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.result"))
        )
     #   print("Result div found!")
    except:
        print("Result div did not appear in time.")

    # Now grab the updated page source
    page = BeautifulSoup(driver.page_source, features='html.parser')
    driver.quit()
    return page


def identifycipher(cipher):
    page = loadwebsite('https://www.dcode.fr/cipher-identifier', 
                   cipher)

    from urllib.parse import urljoin

    base_url = "https://www.dcode.fr"

    data = [
        (a.text.strip(), urljoin(base_url, a.get('href')))
        for r in page.find_all('td', class_='result')[::2]
        if (a := r.find('a'))
    ]

    #print(data[0])
    return data[0]

if __name__ == "__main__":
    import sys
    print(identifycipher(sys.argv[1]))