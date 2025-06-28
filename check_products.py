import json
import os

def filter_and_split_json(input_json_data, output_directory="filtered_jsons"):
    """
    Filters items from a JSON dataset based on specified categories and creates
    separate JSON files for each unique value within those categories.

    Args:
        input_json_data (str): A JSON string containing a list of items.
                                Each item is expected to be a dictionary.
        output_directory (str): The directory where the new JSON files will be saved.
                                 Defaults to "filtered_jsons".
    """
    try:
        items = json.loads(input_json_data)
        if not isinstance(items, list):
            print("Error: Input JSON must be a list of items.")
            return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during JSON loading: {e}")
        return

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    print(f"Output files will be saved in: '{os.path.abspath(output_directory)}'\n")

    # Categories to filter by
    filter_categories = ["bonusMechanism", "nutriscore", "mainCategory"]

    # Dictionary to hold unique types and their counts
    unique_types_summary = {category: {} for category in filter_categories}

    # Process each filter category
    for category in filter_categories:
        print(f"--- Processing by '{category}' ---")
        filtered_data_by_category = {}

        # Group items by the current category's value
        for item in items:
            category_value = item.get(category)
            if category_value is not None:
                # Convert list values to tuple for dictionary key hashing
                if isinstance(category_value, list):
                    category_value_key = tuple(category_value)
                    display_value = str(category_value) # For printing
                else:
                    category_value_key = category_value
                    display_value = category_value # For printing

                if category_value_key not in filtered_data_by_category:
                    filtered_data_by_category[category_value_key] = []
                filtered_data_by_category[category_value_key].append(item)
                
                # Update unique types summary for reporting
                unique_types_summary[category][display_value] = unique_types_summary[category].get(display_value, 0) + 1
            else:
                print(f"Warning: Item missing '{category}' field: {item.get('id', 'No ID provided')}")


        # Save each filtered segment to a new JSON file
        for value_key, segment_items in filtered_data_by_category.items():
            # Create a clean filename
            filename_value = str(value_key).replace(" ", "_").replace("/", "_").replace("\\", "_").replace("'", "").replace('"', '').replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace(",", "")
            output_filename = os.path.join(output_directory, f"{category}_{filename_value}.json")
            
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(segment_items, f, indent=4, ensure_ascii=False)
                print(f"  - Created '{output_filename}' with {len(segment_items)} items.")
            except IOError as e:
                print(f"Error saving file {output_filename}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while saving: {e}")

        print(f"\nTotal unique types for '{category}': {len(filtered_data_by_category)}")
        print("-" * (20 + len(category)) + "\n")


    # Final summary report
    print("--- Overall Summary ---")
    for category, types_data in unique_types_summary.items():
        print(f"'{category}' has {len(types_data)} different types.")
        for type_value, count in types_data.items():
            print(f"  - Type '{type_value}': {count} occurrences in original data.")
    print("-----------------------\n")

# --- Example Usage ---
# To use your own JSON file, uncomment the following lines and
# ensure 'output/bonus_items.json' exists in your script's working directory,
# or provide the full path to the file.
try:
    with open("output/bonus_items.json", 'r', encoding='utf-8') as f:
        my_json_data = f.read()
    filter_and_split_json(my_json_data)
except FileNotFoundError:
    print("Error: 'output/bonus_items.json' not found. Please ensure the file exists at the specified path.")
except Exception as e:
    print(f"An error occurred while reading the input file: {e}")
