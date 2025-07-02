import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# --- Configuration ---
LOCAL_JSON_INPUT_PATH = "data/output/bonus_items.json"  # Your local JSON file path
CHROMA_DB_PATH = "data/chroma_db"  # Directory to store your ChromaDB data
COLLECTION_NAME = "ah_bonus_items"  # Name for your vector collection

# Choose an open-source embedding model from Hugging Face
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Helper Functions ---


def load_json_data(filepath: str) -> list:
    """Loads JSON data from a local file."""
    print(f"Attempting to load JSON data from local path: {filepath}")
    if not os.path.exists(filepath):
        print(f"Error: Local file not found at {filepath}.")
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} items from local file.")
        return data
    except json.JSONDecodeError:
        print(
            f"Error: Could not decode JSON from local file at {filepath}. Check file format.")
        return []
    except Exception as e:
        print(
            f"An unexpected error occurred loading local file {filepath}: {e}")
        return []

# --- Main Workflow ---


def create_vector_database(input_filepath: str, db_path: str, collection_name: str, model_name: str):
    """
    Creates a ChromaDB vector database from a local JSON file.
    """
    all_items = load_json_data(input_filepath)
    if not all_items:
        print("No items to process. Exiting.")
        return

    print(f"Loading embedding model: {model_name}...")
    embedding_model = SentenceTransformer(model_name)
    print("Embedding model loaded.")

    print(f"Initializing ChromaDB client at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)

    try:
        collection = client.get_or_create_collection(
            name=collection_name,
        )
        print(f"ChromaDB collection '{collection_name}' ready.")

        # Group items by mainCategory for batch processing
        items_by_category = {}
        for item in all_items:
            category = item.get('mainCategory', 'Unknown').replace('_', ' ')
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)

        total_added_count = 0
        if collection.count() != len(all_items):  # Check if full database needs to be built
            print(
                f"Adding {len(all_items)} documents to collection '{collection_name}' by category...")
            for category, items_in_category in items_by_category.items():
                print(
                    f"\nProcessing category: '{category}' with {len(items_in_category)} items.")

                documents_to_embed_batch = []
                metadatas_to_add_batch = []
                ids_to_add_batch = []

                for i, item in enumerate(items_in_category):

                    webshop_id = str(item.get('webshopId', ''))
                    title = item.get('title', '')
                    main_category_text = item.get(
                        'mainCategory', '').replace('_', ' ')
                    sub_category = item.get('subCategory', '')
                    brand = item.get('brand', '')
                    description_highlights = item.get(
                        'descriptionHighlights', '')
                    description_full = item.get('descriptionFull', '')
                    # Extract nutriscore
                    nutriscore = item.get('nutriscore', '')

                    # --- Prepare metadata for ChromaDB ---
                    # Create a copy of the item to modify for metadata
                    item_metadata = {"webshopId": webshop_id}

                    combined_text = (
                        f"ID: {webshop_id}. Title: {title}. "
                        f"Main Category: {main_category_text}. Sub Category: {sub_category}. "
                        f"Brand: {brand}. Highlights: {description_highlights}. "
                        # Added nutriscore
                        f"Description: {description_full}. Nutri-score: {nutriscore}. "
                    )
                    documents_to_embed_batch.append(combined_text)
                    # Use the prepared metadata
                    metadatas_to_add_batch.append(item_metadata)
                    ids_to_add_batch.append(webshop_id)

                # Generate embeddings for the entire category batch
                if documents_to_embed_batch:
                    batch_embeddings = embedding_model.encode(
                        documents_to_embed_batch, show_progress_bar=False).tolist()

                    # Add the category batch to ChromaDB
                    collection.add(
                        embeddings=batch_embeddings,
                        documents=documents_to_embed_batch,
                        metadatas=metadatas_to_add_batch,
                        ids=ids_to_add_batch
                    )
                    total_added_count += len(documents_to_embed_batch)
                    print(
                        f"Added {len(documents_to_embed_batch)} items from category '{category}'. Total in DB: {collection.count()}")
                else:
                    print(f"No documents to add for category '{category}'.")

            print(
                f"\nSuccessfully added {total_added_count} documents to the vector database.")
        else:
            print(
                f"Collection '{collection_name}' already contains {collection.count()} documents. Skipping addition.")

    except Exception as e:
        print(f"Error interacting with ChromaDB: {e}")
        return

    print("\nVector database creation complete.")


# --- Script Execution ---
if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOCAL_JSON_INPUT_PATH), exist_ok=True)
    create_vector_database(LOCAL_JSON_INPUT_PATH, CHROMA_DB_PATH,
                           COLLECTION_NAME, EMBEDDING_MODEL_NAME)
