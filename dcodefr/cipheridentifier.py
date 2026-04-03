
from bs4 import BeautifulSoup

def loadwebsite(site, ciphertext):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
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


async def loadplaywrightwebsite(site, ciphertext):

    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )

        page = await browser.new_page()

        # Go to site
        await page.goto(site)

        # Type in ciphertext
        await page.fill("#cipher_identifier_ciphertext", ciphertext)

        # Click analyze button
        await page.click('[data-post="ciphertext,clues"]')

        # Wait for result div
        try:
            await page.wait_for_selector("div.result", timeout=10000)
        except:
            print("Result div did not appear in time.")

        html = await page.content()
        await browser.close()

    return BeautifulSoup(html, features='html.parser')


async def identifycipher(cipher):
    from urllib.parse import urljoin
    page = await loadplaywrightwebsite(
        "https://www.dcode.fr/cipher-identifier",
        cipher
    )

    base_url = "https://www.dcode.fr"

    data = [
        (a.text.strip(), urljoin(base_url, a.get('href')))
        for r in page.find_all('td', class_='result')[::2]
        if (a := r.find('a'))
    ]

    return data[0] if data else ("No result", None)

    #print(data[0])
    return data[0]

if __name__ == "__main__":
    import sys, asyncio
    print(asyncio.run(identifycipher(sys.argv[1])))