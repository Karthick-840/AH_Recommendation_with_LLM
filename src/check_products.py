import json
import os  # Import the os module for path handling
import base64
import requests


def get_image_url_by_width(images_list, target_width=400):
    """
    Finds the image closest to the target_width, downloads it,
    and returns it as a base64-encoded data URI (inline image).
    """
    if not images_list:
        return "https://placehold.co/150x150?text=No+Image"

    best_match = None
    min_diff = float('inf')

    for img in images_list:
        if 'width' in img and 'url' in img:
            width = img['width']
            diff = abs(width - target_width)
            if diff < min_diff:
                min_diff = diff
                best_match = img
            elif diff == min_diff and width > (best_match['width'] if best_match else 0):
                best_match = img

    url = best_match['url'] if best_match else images_list[0].get('url', '')

    # Download the image and convert to base64
    try:
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get(
            'Content-Type', 'image/jpeg')  # default fallback
        encoded = base64.b64encode(response.content).decode('utf-8')
        return f"data:{content_type};base64,{encoded}"
    except Exception as e:
        print(f"Warning: Failed to load image from {url}. Error: {e}")
        return "https://placehold.co/150x150?text=No+Image"


def encode_local_image_to_base64(image_path):
    """Embeds a local image file into a base64 data URI"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return "https://placehold.co/150x150?text=No+Image"

    ext = os.path.splitext(image_path)[-1].lower().replace('.', '')
    if ext not in ['jpg', 'jpeg', 'png']:
        ext = 'jpeg'

    try:
        with open(image_path, 'rb') as img_file:
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
        return f"data:image/{ext};base64,{encoded}"
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return "https://placehold.co/150x150?text=Error"


def generate_product_email_html(products_data):
    """
    Generates a vertically-stacked HTML layout for:
    - Recipe recommendations
    - Product offers
    """

    # === Load Recipe Cards ===
    recipe_cards = []
    try:
        with open("data/output/generated_recipes.json", "r", encoding="utf-8") as rf:
            recipe_data = json.load(rf)

        for recipe in recipe_data.get("recipes", []):
            name = recipe.get("name", "No Title")
            ingredients = recipe.get("ingredients", [])
            instructions = recipe.get("instructions", [])
            image_path = recipe.get(
                "imageUrl", "https://placehold.co/150x150?text=No+Image").replace("\\", "/")
            image_src = encode_local_image_to_base64(image_path)

            ingredients_html = "".join(
                f"<li>{i['name']}</li>" for i in ingredients)
            instructions_html = "".join(
                f"<li>{step}</li>" for step in instructions)

            recipe_card = f"""
            <div class="card">
                <div class="card-content">
                    <img src="{image_src}" alt="{name}" class="card-image">
                    <div class="card-text">
                        <h3>{name}</h3>
                        <strong>Ingredients:</strong>
                        <ul>{ingredients_html}</ul>
                        <strong>Instructions:</strong>
                        <ol>{instructions_html}</ol>
                    </div>
                </div>
            </div>
            """
            recipe_cards.append(recipe_card)
    except Exception as e:
        recipe_cards.append(
            f"<p style='color:red;'>Error loading recipes: {e}</p>")

    # === Generate Product Cards ===
    product_cards = []
    for product in products_data:
        title = product.get("title", "N/A")
        webshop_id = product.get("webshopId", "N/A")
        sales_unit_size = product.get("salesUnitSize", "N/A")
        unit_price_description = product.get("unitPriceDescription", "N/A")
        bonus_start_date = product.get("bonusStartDate", "N/A")
        bonus_end_date = product.get("bonusEndDate", "N/A")
        bonus_mechanism = product.get("bonusMechanism", "N/A")
        main_category = product.get("mainCategory", "N/A")
        sub_category = product.get("subCategory", "N/A")
        discount_labels = product.get("discountLabels", [])

        current_price_raw = product.get('currentPrice')
        price_before_bonus_raw = product.get('priceBeforeBonus')
        price_display_html = ""
        if current_price_raw is not None:
            if price_before_bonus_raw is not None:
                price_display_html = (
                    f'<span class="price-before-bonus">€{price_before_bonus_raw:.2f}</span> '
                    f'<span class="current-price">€{current_price_raw:.2f}</span>'
                )
            else:
                price_display_html = f'<span class="current-price">€{current_price_raw:.2f}</span>'
        elif price_before_bonus_raw is not None:
            price_display_html = f'<span class="current-price">€{price_before_bonus_raw:.2f}</span>'
        else:
            price_display_html = "N/A"

        image_url = get_image_url_by_width(
            product.get("images", []), target_width=400)
        if not image_url:
            image_url = "https://placehold.co/150x150/cccccc/333333?text=No+Image"

        discount_labels_html = ""
        for label in discount_labels:
            desc = label.get("defaultDescription", "")
            amount = label.get("amount")
            if desc:
                discount_labels_html += f'<div class="discount-label">{desc}</div>'
            elif amount is not None:
                discount_labels_html += f'<div class="discount-label">€{amount:.2f} off</div>'

        product_card = f"""
        <div class="card">
            <div class="card-content">
                <img src="{image_url}" alt="{title}" class="card-image">
                <div class="card-text">
                    <h3>{title} ({webshop_id})</h3>
                    <p><strong>Bonus Period:</strong> {bonus_start_date} – {bonus_end_date}</p>
                    <p><strong>Bonus Mechanism:</strong> {bonus_mechanism}</p>
                    <p>{price_display_html}</p>
                    <p><strong>Category:</strong> {main_category} &gt; {sub_category}</p>
                    <p>{sales_unit_size} ({unit_price_description})</p>
                    {discount_labels_html}
                </div>
            </div>
        </div>
        """
        product_cards.append(product_card)

    # === Final HTML Template ===
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recipes & AH Deals</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 20px;
            }}
            h1, h2 {{
                color: #007bff;
            }}
            .card {{
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                margin-bottom: 20px;
                overflow: hidden;
            }}
            .card-content {{
                display: flex;
                flex-direction: row;
                gap: 20px;
                padding: 15px;
            }}
            .card-image {{
                width: 150px;
                height: 150px;
                object-fit: cover;
                border-radius: 8px;
            }}
            .card-text {{
                flex: 1;
            }}
            .price-before-bonus {{
                text-decoration: line-through;
                color: #888;
                font-size: 14px;
            }}
            .current-price {{
                font-weight: bold;
                color: #28a745;
                font-size: 16px;
            }}
            .discount-label {{
                background-color: #ffe0b2;
                color: #e65100;
                padding: 5px 8px;
                border-radius: 4px;
                font-size: 13px;
                display: inline-block;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <h1>🍽️ Recipe Recommendations</h1>
        {''.join(recipe_cards)}

        <h2>🛒 AH Discount Products</h2>
        {''.join(product_cards)}
    </body>
    </html>
    """

    return html_template


with open('data/output/llm_recommended_items_metadata.json', 'r', encoding='utf-8') as f:
    products_to_email = json.load(f)

generated_html = generate_product_email_html(products_to_email)

with open('data/html/generated_email1.html', 'w', encoding='utf-8') as f:
    f.write(generated_html)
