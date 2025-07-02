import json
import os  # Import the os module for path handling


def get_image_url_by_width(images_list, target_width=400):
    """
    Finds the URL for the image closest to the target_width, preferring larger
    if exact match not found.
    """
    if not images_list:
        return ""

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
                # Prefer larger image if difference is the same
                best_match = img

    # Fallback to first URL if no width found
    return best_match['url'] if best_match else images_list[0].get('url', '')


def generate_product_email_html(products_data):
    """
    Generates an HTML string for an email displaying multiple product items
    in a structured, visually appealing format.

    Args:
        products_data (list): A list of dictionaries, where each dictionary
                              represents a single product item with details.

    Returns:
        str: A complete HTML string ready to be used as an email body.
    """
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Product Offers</title>
        <style>
            /* Basic Reset & Body Styles */
            body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
            img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
            a {{ text-decoration: none; }}
            .ExternalClass {{ width: 100%; }}
            .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div {{ line-height: 100%; }}

            /* Container for the whole email */
            .email-container {{
                max-width: 600px;
                margin: auto;
                background-color: #ffffff;
                font-family: 'Inter', Helvetica, Arial, sans-serif;
                color: #333333;
                border-radius: 8px;
                overflow: hidden; /* For rounded corners */
            }}
            /* Header */
            .header {{
                background-color: #007bff;
                color: #ffffff;
                padding: 20px;
                text-align: center;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }}
            /* Product Item Styling */
            .product-item {{
                background-color: #f9f9f9;
                border: 1px solid #eeeeee;
                border-radius: 8px;
                margin-bottom: 20px;
                padding: 15px;
            }}
            .product-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .product-image-cell {{
                width: 30%;
                vertical-align: top;
                padding-right: 15px;
            }}
            .product-details-cell {{
                width: 45%;
                vertical-align: top;
                padding-right: 15px;
            }}
            .product-discount-cell {{
                width: 25%;
                vertical-align: top;
                text-align: right;
            }}
            .product-image {{
                max-width: 100%;
                height: auto;
                display: block;
                border-radius: 6px;
            }}
            .product-title {{
                font-size: 18px;
                font-weight: bold;
                margin-top: 0;
                margin-bottom: 5px;
                color: #007bff;
            }}
            .product-info {{
                font-size: 14px;
                margin-bottom: 3px;
                line-height: 1.4;
            }}
            .price-before-bonus {{
                text-decoration: line-through;
                color: #888888;
                font-size: 13px;
            }}
            .current-price {{
                font-size: 16px;
                font-weight: bold;
                color: #28a745; /* Green for current price */
            }}
            .discount-label {{
                background-color: #ffe0b2; /* Light orange */
                color: #e65100; /* Darker orange */
                padding: 5px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                display: inline-block; /* Allows multiple labels to stack */
                margin-bottom: 5px;
                line-height: 1.2;
            }}
            .footer {{
                background-color: #f1f1f1;
                color: #666666;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f4f4f4;">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" class="email-container">
                        <!-- Header -->
                        <tr>
                            <td class="header">
                                <h1>AH discount this week!</h1>
                            </td>
                        </tr>
                        <!-- Product Listings -->
                        <tr>
                            <td style="padding: 20px;">
                                {products_html}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td class="footer">
                                <p>&copy; 2025 Your Company. All rights reserved.</p>
                                <p>This email was sent to you because you opted in to receive special offers.</p>
                                <p>Prices are subject to change. See terms and conditions for details.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    products_html_snippets = []
    for product in products_data:
        # Safely get product details
        title = product.get("title", "N/A")
        webshop_id = product.get("webshopId", "N/A")
        sales_unit_size = product.get("salesUnitSize", "N/A")
        unit_price_description = product.get("unitPriceDescription", "N/A")
        bonus_start_date = product.get("bonusStartDate", "N/A")
        bonus_end_date = product.get("bonusEndDate", "N/A")
        bonus_mechanism = product.get("bonusMechanism", "N/A")

        # Get raw price values to check for existence
        current_price_raw = product.get('currentPrice')
        price_before_bonus_raw = product.get('priceBeforeBonus')

        # Price display logic:
        price_display_html = ""
        if current_price_raw is not None:
            # If currentPrice exists, display priceBeforeBonus (if exists) struck through, then currentPrice
            if price_before_bonus_raw is not None:
                price_display_html = (
                    f'<span class="price-before-bonus">€{price_before_bonus_raw:.2f}</span> '
                    f'<span class="current-price">€{current_price_raw:.2f}</span>'
                )
            else:
                # If only currentPrice is available
                price_display_html = f'<span class="current-price">€{current_price_raw:.2f}</span>'
        else:
            # If currentPrice is not available, display priceBeforeBonus (if exists) as the main price, not struck through
            if price_before_bonus_raw is not None:
                price_display_html = f'<span class="current-price">€{price_before_bonus_raw:.2f}</span>'
            else:
                price_display_html = "N/A"  # Fallback if neither price is available

        main_category = product.get("mainCategory", "N/A")
        sub_category = product.get("subCategory", "N/A")
        discount_labels = product.get("discountLabels", [])

        # Get appropriate image URL
        image_url = get_image_url_by_width(
            product.get("images", []), target_width=400)
        if not image_url:  # Fallback to a placeholder if no image URL is found
            image_url = "https://placehold.co/400x400/cccccc/333333?text=No+Image"

        discount_labels_html = ""
        for label in discount_labels:
            desc = label.get("defaultDescription", "")
            amount = label.get("amount")
            if desc:
                discount_labels_html += f'<span class="discount-label">{desc}</span><br>'
            elif amount is not None:
                discount_labels_html += f'<span class="discount-label">€{amount:.2f} off</span><br>'

        product_snippet = f"""
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" class="product-item">
            <tr>
                <td class="product-image-cell">
                    <img src="{image_url}" alt="{title}" width="150" height="150" class="product-image">
                </td>
                <td class="product-details-cell">
                    <p class="product-title">{title} ({webshop_id})</p>
                    <p class="product-info"><strong>Bonus Period:</strong> {bonus_start_date} to {bonus_end_date}</p>
                    <p class="product-info"><strong>Bonus Mechanism:</strong> {bonus_mechanism}</p>
                    <p class="product-info">{price_display_html}</p>
                    <p class="product-info"><strong>Category:</strong> {main_category} &gt; {sub_category}</p>
                    <p class="product-info">{sales_unit_size} ({unit_price_description})</p>
                </td>
                <td class="product-discount-cell">
                    {discount_labels_html}
                </td>
            </tr>
        </table>
        """
        products_html_snippets.append(product_snippet)

    return html_template.format(products_html="".join(products_html_snippets))


# --- Example Usage ---
# Path to your input JSON file
input_json_file_path = "data/output/llm_recommended_items_metadata.json"
# Define the output HTML file path
output_html_file_path = "data/html/generated_email.html"

try:
    with open(input_json_file_path, 'r', encoding='utf-8') as f:
        # Use json.load directly as the file contains the list
        products_to_email = json.load(f)

    # Generate the HTML
    generated_html = generate_product_email_html(products_to_email)

    # Save the generated HTML to a file instead of printing
    with open(output_html_file_path, 'w', encoding='utf-8') as f:
        f.write(generated_html)

    print(
        f"Generated HTML email saved to: {os.path.abspath(output_html_file_path)}")

except FileNotFoundError:
    print(f"Error: The file '{input_json_file_path}' was not found.")
    print("Please ensure you have run the previous JSON filtering script to create this file.")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON from '{input_json_file_path}': {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
