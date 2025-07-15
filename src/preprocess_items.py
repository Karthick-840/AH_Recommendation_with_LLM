import json
from collections import Counter
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential


def get_category_metrics(items):
    """
    Extracts metrics (unique values and their counts) for specified categories
    from a JSON dataset.
    """
    print("--- Starting Metric Extraction ---")

    # Read your actual JSON data from file

    # Categories to extract metrics for
    filter_categories = ["bonusMechanism", "nutriscore", "mainCategory"]

    # Dictionary to hold unique types and their counts for each category
    # Using collections.defaultdict(collections.Counter) for efficiency
    metrics = {cat: Counter(item.get(cat) if not isinstance(item.get(cat), list) else tuple(item.get(cat))
                            for item in items if item.get(cat) is not None) for cat in filter_categories}

    return metrics


def get_bonus_formula(unique_bonus_mechanisms):

    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1"  # The LLM model to use
    token = os.environ["GITHUB_TOKEN"]

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )

    user_prompt = f"""
    I need a Python dictionary named `bonus_mechanism_formulas`.

    For each string in the following `unique_bonus_mechanisms` list, the dictionary **key must be the exact bonus mechanism string**, and the **value must be a Python lambda function**.

    This lambda function must:
    1.  **Explicitly take `PriceBeforeBonus` as its single argument.**
    2.  Calculate the **effective unit price** after the bonus, based on the `PriceBeforeBonus`.

    **Important Assumptions for Generating Formulas:**
    - Unless explicitly stated in the bonus mechanism, assume `PriceBeforeBonus` refers to the **unit price of one item**.
    - For "N for X.XX" deals (e.g., '3 voor 5.00', '2 voor 3.99'), the lambda should return the **effective unit price** (X.XX / N).
    - For "N% korting" or "N% volume voordeel", the formula is `PriceBeforeBonus * (1 - N/100)`.
    - For "X + Y gratis", assume you buy X items and get Y free. The effective unit price is `(PriceBeforeBonus * X) / (X + Y)`.
    - For "N gram voor X.XX" (e.g., '100 GRAM VOOR 1.69'): **Assume `PriceBeforeBonus` provided to the lambda IS the price for N grams.** If `PriceBeforeBonus` is not per N grams, this formula will be incorrect, and external item weight data would be needed in a real application.
    - For ambiguous terms like 'BONUS' or 'stapelen tot X%', the lambda should simply return `PriceBeforeBonus` (i.e., no explicit discount from this term alone, or use the best-case percentage if specified).
    - For 'VOOR X.XX' (e.g., 'VOOR 2.99'), assume X.XX is the new fixed unit price, so the lambda should return `X.XX`.
    - For 'X euro korting' (e.g., '1 euro korting'), assume it's a fixed discount off the PriceBeforeBonus, so `PriceBeforeBonus - X`.

    Please provide only the Python dictionary `bonus_mechanism_formulas` and dont output a Python code in your response. No extra text or explanation beyond comments within the code.

    Here is the list of unique bonus mechanisms:
    {unique_bonus_mechanisms}
    """

    print("Sending request to LLM...")
    response = client.complete(
        messages=[
            SystemMessage("You are a Python expert specializing in retail pricing logic. Provide concise, runnable Python lambda functions for pricing calculations based on natural language descriptions."),
            UserMessage(user_prompt),
        ],
        temperature=0.1,  # Keep temperature low for more deterministic code
        top_p=0.9,
        model=model
    )

    # Extract and print the generated code
    print("\n--- LLM Generated Python Code (Draft) ---")
    generated_code = response.choices[0].message.content
    print(generated_code)
    local_vars = {}
    exec(generated_code, {}, local_vars)
    bonus_mechanism_formulas = local_vars.get("bonus_mechanism_formulas", {})
    print(bonus_mechanism_formulas)
    print("---------------------------------")

    return bonus_mechanism_formulas


def calculate_price_and_savings(item, bonus_mechanism_formulas):

    if 'currentPrice' in item and item['currentPrice'] is not None:
        if 'priceBeforeBonus' in item and item['priceBeforeBonus'] is not None:
            item['calculatedSavings'] = item['priceBeforeBonus'] - \
                item['currentPrice']
        return item

    price_before_bonus = item.get('priceBeforeBonus')
    if price_before_bonus is None:
        # item['currentPrice'] = None
        item['calculatedSavings'] = None
        item['priceCalculationMethod'] = "MissingPriceBeforeBonus"
        return item

    # Handle list or string
    bonus = item.get('bonusMechanism')
    bonus = bonus[0] if isinstance(bonus, list) and bonus else bonus
    formula = bonus_mechanism_formulas.get(bonus)

    if formula:
        try:
            current_price = formula(price_before_bonus)
            item['currentPrice'] = current_price
            item['calculatedSavings'] = price_before_bonus - current_price
            item['priceCalculationMethod'] = f"Formula_{bonus}"
        except Exception:
            item['currentPrice'] = price_before_bonus
            item['calculatedSavings'] = 0.0
            item['priceCalculationMethod'] = f"FormulaError_{bonus}"
    else:
        item['currentPrice'] = price_before_bonus
        item['calculatedSavings'] = 0.0
        item['priceCalculationMethod'] = "NoFormulaFound"

    print(item['currentPrice'],
          item['calculatedSavings'], item['priceCalculationMethod'])
    return item

    # --- Example Usage ---


if __name__ == "__main__":
    try:
        with open("data/output/bonus_items.json", 'r', encoding='utf-8') as f:
            my_json_data = f.read()
        try:
            items = json.loads(my_json_data)
            if not isinstance(items, list):
                print("Error: Input JSON must be a list of items.")

        except Exception as e:
            print(f"An unexpected error occurred during JSON loading: {e}")

    except Exception as e:
        print(f"An unexpected error occurred during JSON loading: {e}")

    # Get the metrics
    all_metrics = get_category_metrics(items)

    unique_bonus_mechanisms = sorted({item.get(
        "bonusMechanism") for item in items if item.get("bonusMechanism") is not None})

    bonus_mechanism_formulas = get_bonus_formula(unique_bonus_mechanisms)

    for item in items:
        calculate_price_and_savings(item, bonus_mechanism_formulas)

with open("data/output/bonus_items_processed.json", "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)
