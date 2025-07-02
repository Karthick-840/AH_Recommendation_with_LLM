import os
import re
import shutil
from icrawler.builtin import GoogleImageCrawler
import json


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
    google_crawler.crawl(keyword=search_term, max_num=1)

    # Get first downloaded image file (icrawler names them like 000001.jpg)
    downloaded_files = [f for f in os.listdir(
        temp_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not downloaded_files:
        print("No image downloaded.")
        return None

    original_file_path = os.path.join(temp_dir, downloaded_files[0])
    # Rename to match the search term
    clean_name = sanitize_filename(title)
    final_file_path = os.path.join(save_dir, f"{clean_name}.jpg")

    shutil.move(original_file_path, final_file_path)

    # Clean up temp directory if empty
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass  # Directory not empty or other issue

    print(f"Image saved as: {final_file_path}")
    return final_file_path


with open('data/output/generated_recipes.json', 'r', encoding='utf-8') as f:
    generated_recipes = json.load(f)

for recipe in generated_recipes.get('recipes', []):
    recipe_title = recipe.get('name')
    recipe_description = recipe.get('description')
    if recipe_title:
        image_url = download_and_rename_image(recipe_title, recipe_description)
        recipe['imageUrl'] = image_url  # Add imageUrl to the recipe object
    else:
        recipe['imageUrl'] = ""  # Add empty string if no name


recommended_items_output_filename = "data/output/new_generated_recipes.json"
with open(recommended_items_output_filename, 'w', encoding='utf-8') as f:
    json.dump(generated_recipes, f, indent=2)
