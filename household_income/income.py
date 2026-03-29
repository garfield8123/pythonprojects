import pdfplumber

def contains_county(data):
    return (
        bool(data) and
        bool(data[0]) and
        isinstance(data[0][0], str) and
        "county" in data[0][0].lower()
    )

def incomedata(data, numofhouseholds):
    fullincomedict = {}
    with pdfplumber.open(data) as pdf:
        for p in pdf.pages:
            for t in p.extract_tables():
                if len(t) > 4:
                    if contains_county(t):
                        county = t[0][0].split("\n")[0]
                        incomedict = {}
                        for r in t:
                            incomedict.update({r[1]: r[1+numofhouseholds]})
                        fullincomedict.update({county:incomedict})
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


def getincomedata(numofhousehold, county):
    downloadpdf("https://www.hcd.ca.gov/sites/default/files/docs/grants-and-funding/income-limits-2025.pdf", "income-limits-2025.pdf")
    return incomedata("income-limits-2025.pdf", numofhousehold).get(county)


#https://www.hcd.ca.gov/sites/default/files/docs/grants-and-funding/income-limits-2025.pdf

if __name__ == "__main__":
    print("Alameda County: ", getincomedata(1,"Alameda County"))
    print("San Francisco County: ", getincomedata(1,"San Francisco County"))
    print("Santa Clara County: ", getincomedata(1,"Santa Clara County"))
    print("San Mateo County: ", getincomedata(1,"San Mateo County"))
    print("Contra Costa County: ", getincomedata(1,"Contra Costa County"))
