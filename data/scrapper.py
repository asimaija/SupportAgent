import requests
import trafilatura
import csv
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    "cloud_services": "https://appinsnap.com/services/digital-infrastructure-services/cloud-services",
    "noc_soc": "https://appinsnap.com/services/digital-infrastructure-services/noc-and-soc-services",
    "datacenter": "https://appinsnap.com/services/digital-infrastructure-services/datacenter-services",
    "backup_disaster_recovery": "https://appinsnap.com/services/digital-infrastructure-services/backup-and-disaster-recovery-services",
    "application_integration": "https://appinsnap.com/services/digital-technology-services/application-integration-services",
    "application_modernization": "https://appinsnap.com/services/digital-technology-services/application-modernization-services",
    "smart_traffic_enforcement": "https://appinsnap.com/products/smart-traffic-enforcement-system",
}

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "dataset" / "appinsnap.csv"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_category(name):

    if name in ["home", "about", "contact"]:
        return "company"

    if "policy" in name or name == "terms_conditions":
        return "policy"

    if name == "faq":
        return "faq"

    if name in ["services", "solutions"]:
        return "service"

    if name in [
        "cloud_services",
        "noc_soc",
        "datacenter",
        "backup_disaster_recovery",
        "application_integration",
        "application_modernization"
    ]:
        return "service"

    if name == "smart_traffic_enforcement":
        return "product"

    return "other"


def scrape_page(name, url):

    try:
        print(f"Scraping: {url}")

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
            include_formatting=True
        )

        if not text:
            print("No content found")
            return None

        return text

    except requests.exceptions.RequestException as error:
        print(f"Request error: {error}")
        return None

    except Exception as error:
        print(f"Error: {error}")
        return None


def main():

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "id",
            "category",
            "title",
            "source",
            "content"
        ])

        record_id = 1

        for name, url in PAGES.items():

            content = scrape_page(name, url)

            if content:

                writer.writerow([
                    record_id,
                    get_category(name),
                    name.replace("_", " ").title(),
                    url,
                    content
                ])

                record_id += 1

    print("\nCSV created successfully!")
    print(f"File: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()