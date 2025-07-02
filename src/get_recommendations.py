import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
import asyncio
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from googlesearch.googlesearch import GoogleSearch
from icrawler.builtin import GoogleImageCrawler
import json
import os
import re
import shutil


def sanitize_filename(text):
    """Remove or replace characters not allowed in filenames."""
    return re.sub(r'[\\/*?:"<>|&]', "", text)


def download_and_rename_image(title, description):
    # Ensure directory exists
    save_dir = "data/img/receipe_img"
    os.makedirs(save_dir, exist_ok=True)

    # Temporary directory to store initial download
    temp_dir = os.path.join(save_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Run crawler to download 1 image
    search_term = title+description
    google_crawler = GoogleImageCrawler(storage={'root_dir': temp_dir})
    google_crawler.crawl(keyword=search_term, max_num=5)

    # Get first downloaded image file (icrawler names them like 000001.jpg)
    downloaded_files = sorted([
        f for f in os.listdir(temp_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    if not downloaded_files:
        print("No image downloaded.")
        return None

    original_file_path = os.path.join(temp_dir, downloaded_files[0])
    # Rename to match the search term
    clean_name = sanitize_filename(title)
    final_file_path = os.path.join(save_dir, f"{clean_name}.jpg")

    shutil.move(original_file_path, final_file_path)

    # Clean up temp dir
    for f in downloaded_files[1:]:
        try:
            os.remove(os.path.join(temp_dir, f))
        except:
            pass
    try:
        os.rmdir(temp_dir)
    except:
        pass

    print(f"Image saved as: {final_file_path}")
    return final_file_path


# --- Configuration ---
CHROMA_DB_PATH = "data/chroma_db"
CHROMA_COLLECTION_NAME = "ah_bonus_items"
# Must match model used for DB creation
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# Grok-3 LLM Configuration
GROK_ENDPOINT = "https://models.github.ai/inference"
GROK_MODEL = "xai/grok-3"
try:
    GROK_TOKEN = os.environ["GITHUB_TOKEN"]
except KeyError:
    print("ERROR: GITHUB_TOKEN environment variable not set. Please set it.")
    exit(1)

# --- Main Workflow Function ---


async def find_recipe_image(recipe_name: str) -> str:
    """
    Uses Google Search to find an image URL for a given recipe name.
    Returns the URL of the first image found, or an empty string if none.
    """
    print(f"Searching for image for recipe: '{recipe_name}'...")
    try:
        # Perform a Google search specifically for images
        # The 'search' tool typically returns text snippets and URLs.
        # We'll look for URLs that seem like image links.
        response = GoogleSearch().search(recipe_name)
        for result in response.results:
            print(result)
            print("Title: " + result.title)
            print("Content: " + result.getText())

        if response and results[0].results:
            for res in results[0].results:
                if res.url and ('.jpg' in res.url.lower() or '.png' in res.url.lower() or '.jpeg' in res.url.lower()):
                    print(f"Found image URL: {res.url}")
                    return res.url
            # If no direct image URL found, try to return the URL of the first result's page
            if results[0].results[0].url:
                print(
                    f"No direct image URL found, returning first page URL: {results[0].results[0].url}")
                return results[0].results[0].url
        print("No image found for this recipe.")
        return ""
    except Exception as e:
        print(f"Error during image search for '{recipe_name}': {e}")
        return ""


async def get_product_suggestions(user_query: str):
    """
    Uses Grok-3 LLM to suggest products/items based on a user query,
    formatted in English and Dutch, and saves them to a JSON file.
    """
    client = ChatCompletionsClient(
        endpoint=GROK_ENDPOINT, credential=AzureKeyCredential(GROK_TOKEN))

    system_prompt_content = (
        "You are an expert in food and nutrition. Based on the user's request, "
        "suggest up to 15 relevant food products or ingredients. "
        "For each product, provide its name in English, followed by its Dutch translation in parentheses, separated by a comma. "
        "Example: 'Chicken Breast (Kipfilet), Eggs (Eieren), Broccoli (Broccoli)'."
        "Provide the output as a JSON object with a single key 'products' which is an array of these product strings."
    )

    user_message_content = f"""
    User's request: "{user_query}"

    Please provide the product suggestions in the following JSON format:
    {{
  "products_string": "Product 1 English (Product 1 Dutch), Product 2 English (Product 2 Dutch)"
    }}
    """
    print(
        f"\nCalling Grok-3 LLM for product suggestions based on: '{user_query}'")
    try:
        response = client.complete(  # Use await here as client.complete is async
            messages=[
                SystemMessage(system_prompt_content),
                UserMessage(user_message_content),
            ],
            temperature=0.7,
            top_p=1.0,
            model=GROK_MODEL
        )

        print(response)
        products_json_text = response.choices[0].message.content
        suggested_products_obj = json.loads(products_json_text)
        # Extract the string from the JSON object
        suggested_products_string = suggested_products_obj.get(
            "products_string", "")
        print("Successfully received product suggestions from Grok-3 LLM.")
        # Return as a dictionary for consistency in saving
        return {"products_string": suggested_products_string}
    except json.JSONDecodeError:
        print(
            f"Error decoding JSON from Grok-3 LLM response. Raw: {products_json_text[:500]}...")
        return {"products_string": ""}
    except Exception as e:
        print(f"An error occurred during Grok-3 API call: {e}")
        return {"products_string": ""}


async def generate_recipes_from_chromadb(user_query_prompt: str):
    # 1. Initialize embedding model for user query
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # 2. Connect to ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
    print(f"Connected to ChromaDB collection '{CHROMA_COLLECTION_NAME}'.")

    # 3. Generate embedding for the user's query
    query_embedding = embedding_model.encode([user_query_prompt]).tolist()[0]

    # 4. Query ChromaDB for relevant items, including metadata
    # Retrieve top N semantically relevant items directly
    # Adjust this number (20-50 as per your previous guidance)
    num_items_for_recipe_generation = 50
    chroma_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=num_items_for_recipe_generation,
        include=['metadatas']
    )

    # Directly use the semantically relevant items from ChromaDB for recipe generation
    # These 'item_meta' objects contain the metadata stored in ChromaDB (e.g., {"webshopId": ...})
    semantically_relevant_chromadb_metadata = chroma_results['metadatas'][
        0] if chroma_results and chroma_results['metadatas'] else []

    if not semantically_relevant_chromadb_metadata:
        print("No relevant items found in ChromaDB. Cannot suggest recipes.")
        return

    print(
        f"\nFound {len(semantically_relevant_chromadb_metadata)} semantically relevant items from ChromaDB.")
    filter_ids = {int(d['webshopId'])
                  for d in semantically_relevant_chromadb_metadata}

    print(f"\nTheir WebShop IDs are {len(filter_ids)}.")

    # 5. Retrieve full item details from original JSON using webshopId from ChromaDB metadata
    items_for_llm = []

    try:
        with open('data/output/bonus_items.json', 'r', encoding='utf-8') as f:
            original_bonus_items = json.load(f)
        items_for_llm = [item for item in original_bonus_items if int(
            item.get('webshopId', -1)) in filter_ids]
    except Exception as e:
        print(f"Error loading original JSON for full details lookup: {e}")
        return

    if not items_for_llm:
        print("No full item details retrieved for recipe generation. Check original JSON and IDs.")
        return

    print(
        f"Selected {len(items_for_llm)} full items for LLM processing (titles):")
    for item in items_for_llm:
        print(f"- {item.get('title', 'N/A')}")

    # 6. Prepare prompt for Grok-3 LLM using full item details
    item_summaries_for_llm = []
    for item in items_for_llm:
        title = item.get('title', 'N/A')
        webshop_id = item.get('webshopId', item.get(
            'id', 'N/A'))  # Get webshopId
        main_category = item.get('mainCategory', '').replace('_', ' ')
        nutriscore = item.get('nutriscore', 'N/A')
        # Removed explicit "DiscountInfo" as it's not a primary filter here
        item_summaries_for_llm.append(
            f"- {title} (Category: {main_category}, Nutri-score: {nutriscore}, webshop_id: {webshop_id})")

    items_list_str = "\n".join(item_summaries_for_llm)

    client = ChatCompletionsClient(
        endpoint=GROK_ENDPOINT, credential=AzureKeyCredential(GROK_TOKEN))

    # System prompt incorporating user query and available items from ChromaDB
    system_prompt_content = (
        f"You are an expert chef and nutritionist. Based on the user's request: '{user_query_prompt}', "
        "and the following ONLY available ingredients from a supermarket (retrieved via semantic search from a vector database), "
        "generate 3-4 simple, healthy, and creative recipe ideas. Focus on using these specific ingredients effectively and reducing food waste. "
        "For each ingredient in the recipe, you MUST include its 'webshopId' from the provided list. Do not list a ingredient for which there is no WebShopId "
        "Provide the output as a JSON object containing an array of recipe objects."
    )
    user_message_content = f"""
Available ingredients:
{items_list_str}

Please provide the recipes in the following JSON format:
{{
  "recipes": [
    {{
      "name": "Recipe Name",
      "description": "Brief description of the recipe.",
      "ingredients": [
        {{"name": "Ingredient 1 with quantity", "webshopId": "ID_OF_INGREDIENT_1"}},
        {{"name": "Ingredient 2 with quantity", "webshopId": "ID_OF_INGREDIENT_2"}}
      ],
      "instructions": ["1. Step one.", "2. Step two."]
    }}
  ]
}}
"""

    # 7. Generate recipes using Grok-3 LLM
    print("\nCalling Grok-3 LLM for recipe generation...")
    try:
        response = client.complete(
            messages=[SystemMessage(system_prompt_content),
                      UserMessage(user_message_content)],
            temperature=0.7, top_p=1.0, model=GROK_MODEL
        )
        recipes_json_text = response.choices[0].message.content
        generated_recipes = json.loads(recipes_json_text)
        print("Successfully received recipes from Grok-3 LLM.")
    except Exception as e:
        print(f"Error generating recipes with Grok-3: {e}")
        generated_recipes = {"recipes": []}

    for recipe in generated_recipes.get('recipes', []):
        recipe_title = recipe.get('name')
        recipe_description = recipe.get('description')
    if recipe_title:
        image_url = download_and_rename_image(recipe_title, recipe_description)
        recipe['imageUrl'] = image_url  # Add imageUrl to the recipe object
    else:
        recipe['imageUrl'] = ""  # Add empty string if no name

# 8. Save recipes to JSON
    recipes_output_filename = "data/output/generated_recipes.json"
    with open(recipes_output_filename, 'w', encoding='utf-8') as f:
        json.dump(generated_recipes, f, indent=2)
    print(f"Generated recipes saved to '{recipes_output_filename}'")

    #

# This section now directly uses the webshopId from the LLM's output
    llm_recommended_item_ids = []
    for recipe in generated_recipes.get('recipes', []):
        for ingredient_obj in recipe.get('ingredients', []):
            if isinstance(ingredient_obj, dict) and 'webshopId' in ingredient_obj:
                llm_recommended_item_ids.append(
                    int(ingredient_obj['webshopId']))
    print(llm_recommended_item_ids)

    filtered_items_to_save = [item for item in items_for_llm if int(
        item.get('webshopId', -1)) in llm_recommended_item_ids]

    recommended_items_output_filename = "data/output/llm_recommended_items_metadata.json"
    with open(recommended_items_output_filename, 'w', encoding='utf-8') as f:
        json.dump(filtered_items_to_save, f, indent=2)
    print(
        f"Metadata for {len(filtered_items_to_save)} LLM-recommended items saved to '{recommended_items_output_filename}'")

# --- Script Execution ---

if __name__ == "__main__":
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    user_query = "I am Indian, I want healthy, high-fiber options vegetarian but not Vegan and I want recommendations for Lunch recipes post intermittent fasting."

    if "GITHUB_TOKEN" not in os.environ:
        print("Please set the GITHUB_TOKEN environment variable with your token from models.github.ai.")
        print("Example: export GITHUB_TOKEN='your_token_here'")
    elif GROK_TOKEN == "YOUR_API_KEY_HERE":
        print("ERROR: Replace 'YOUR_API_KEY_HERE' in the script with your actual GITHUB_TOKEN value or ensure it's loaded from os.environ.")
    else:
        product_recommendations = asyncio.run(
            get_product_suggestions(user_query))
        print(product_recommendations)
        asyncio.run(generate_recipes_from_chromadb(
            f"For this {user_query}, use these {product_recommendations} for receipe creation"))
