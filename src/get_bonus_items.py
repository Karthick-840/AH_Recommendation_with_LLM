import requests
import argparse
import json
import os
import logging

module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)


def get_token():
    url = "https://api.ah.nl/mobile-auth/v1/auth/token/anonymous"
    body = {"clientId": "appie"}
    headers = {
        "User-Agent": "Appie/8.22.3",
        "X-Application": "AHWEBSHOP",
        "X-Client-Name": "ah-web",
        "X-Client-Version": "1.0.0",
        "Accept": "application/json"
    }
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_bonus_items(token, page=0, size=100):
    url = "https://api.ah.nl/mobile-services/product/search/v2"
    params = {
        "bonus": "ANY",
        "availableOnline": "true",
        "page": page,
        "size": size
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Appie/8.22.3",
        "X-Application": "AHWEBSHOP",
        "X-Client-Name": "ah-web",
        "X-Client-Version": "1.0.0",
        "Accept": "application/json"
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get("products", [])


def get_all_bonus_items(config=None):

    current_logger = module_logger

    if not config:
        json_save_path = os.path.join("data/output", "bonus_items.json")
        current_logger.info("No Configuration received")

    else:
        json_save_path = config['file_paths']['bonus_items_save_path']

    token = get_token()
    all_bonus_products = []
    page = 0
    size = 100  # max items per request
    max_pages = 20  # limit pagination

    while page < max_pages:
        current_logger.info(f"Fetching page {page}...")
        products = fetch_bonus_items(token, page=page, size=size)
        if not products:
            break
        filter_bonus = [p for p in products if p.get("isBonus")]
        # all_products.extend(products)
        all_bonus_products.extend(filter_bonus)
        page += 1

    with open(json_save_path, "w", encoding="utf-8") as f:
        json.dump(all_bonus_products, f, ensure_ascii=False, indent=2)
    current_logger.info(
        f"✅ Saved {len(all_bonus_products)} items to {json_save_path}")

    return all_bonus_products


    # --- Script Execution ---
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # module_logger = logging.getLogger("get_bonus.py")
    module_logger.info("Running get_bonus.py directly.")
    get_all_bonus_items()
