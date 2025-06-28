import requests
import json
import os

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

def save_as_json(data, filename="bonus_items.json"):
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(data)} items to output/{filename}")

def get_all_bonus_items():
    token = get_token()
    all_products = []
    page = 0
    size = 100  # max items per request
    max_pages = 20  # limit pagination

    while page < max_pages:
        print(f"Fetching page {page}...")
        products = fetch_bonus_items(token, page=page, size=size)
        if not products:
            break
        all_products.extend(products)
        page += 1

    return all_products

def filter_bonus_products(products):
    # Keeps only products where isBonus == True
    return [p for p in products if p.get("isBonus")]

def main():
    all_items = get_all_bonus_items()
    bonus_items = filter_bonus_products(all_items)
    save_as_json(bonus_items)

if __name__ == "__main__":
    main()
