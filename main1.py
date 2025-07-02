import asyncio
from src.get_embeddings import filter_local_json_items

if __name__ == "__main__":
    # >>> USER INPUT REQUIRED <<<
    # Set the path to your local JSON input file
    # <--- **SET YOUR INPUT FILE PATH HERE**
    LOCAL_JSON_INPUT_PATH = "data/output/bonus_items.json"
    # Set the path for the output JSON file
    # <--- **SET YOUR OUTPUT FILE PATH HERE**
    LOCAL_JSON_OUTPUT_PATH = "filtered_bonus_items.json"

    if LOCAL_JSON_INPUT_PATH == "data/output/bonus_items.json":
        print("WARNING: Please ensure 'data/output/bonus_items.json' exists or update LOCAL_JSON_INPUT_PATH.")
        # Optional: create a dummy file for testing if it doesn't exist
        # This part is removed as per your direct instruction, but be aware
        # the script will fail if the input file doesn't exist.

    asyncio.run(filter_local_json_items(
        LOCAL_JSON_INPUT_PATH, LOCAL_JSON_OUTPUT_PATH))
    print("\nFiltering process completed.")
