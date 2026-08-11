import requests
import trafilatura
import urllib3
from pathlib import Path


# Disable SSL warnings
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# ============================================================
# WEBSITE PAGES
# ============================================================

PAGES = {
    "home": "https://appinsnap.com/",
    "about": "https://appinsnap.com/about-us",
    "contact": "https://appinsnap.com/contact",
    "faq": "https://appinsnap.com/frequently-asked-questions",
    "shipping_policy": "https://appinsnap.com/shipping-policy",
    "terms_conditions": "https://appinsnap.com/terms-and-conditions",
    "return_policy": "https://appinsnap.com/return-policy",
    "privacy_policy": "https://appinsnap.com/privacy-policy",
    "refund_policy": "https://appinsnap.com/refund-policy",

    "services": "https://appinsnap.com/services",
    "solutions": "https://appinsnap.com/solutions",

    "cloud_services":
        "https://appinsnap.com/services/digital-infrastructure-services/cloud-services",

    "noc_soc":
        "https://appinsnap.com/services/digital-infrastructure-services/noc-and-soc-services",

    "datacenter":
        "https://appinsnap.com/services/digital-infrastructure-services/datacenter-services",

    "backup_disaster_recovery":
        "https://appinsnap.com/services/digital-infrastructure-services/backup-and-disaster-recovery-services",

    "application_integration":
        "https://appinsnap.com/services/digital-technology-services/application-integration-services",

    "application_modernization":
        "https://appinsnap.com/services/digital-technology-services/application-modernization-services",

    "smart_traffic_enforcement":
        "https://appinsnap.com/products/smart-traffic-enforcement-system",
}


# ============================================================
# OUTPUT FILE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = BASE_DIR / "dataset"

DATASET_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TXT_FILE = DATASET_DIR / "appinsnap.txt"


# ============================================================
# HTTP HEADERS
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ============================================================
# SCRAPE PAGE
# ============================================================

def scrape_page(name, url):

    try:

        print(f"Scraping: {name}")

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
            verify=False
        )

        response.raise_for_status()

        text = trafilatura.extract(
            response.text,
            include_links=False,
            include_images=False,
            include_tables=True,
            include_formatting=False
        )

        if not text:
            print("No content found")
            return None

        return text.strip()

    except requests.exceptions.RequestException as error:

        print(f"Request error: {error}")
        return None

    except Exception as error:

        print(f"Error: {error}")
        return None


# ============================================================
# CREATE TXT FILE
# ============================================================

def create_txt():

    with open(
        TXT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for name, url in PAGES.items():

            content = scrape_page(
                name,
                url
            )

            if content:

                title = name.replace(
                    "_",
                    " "
                ).title()

                file.write(
                    f"TITLE: {title}\n"
                )

                file.write(
                    f"SOURCE: {url}\n\n"
                )

                file.write(content)

                file.write(
                    "\n\n"
                    + "=" * 80
                    + "\n\n"
                )

                print(
                    f"Saved: {title}"
                )

    print("\nTXT created successfully!")
    print(f"File: {TXT_FILE}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("APPINSNAP TEXT SCRAPER")
    print("=" * 60)

    create_txt()

    print("\nDone!")