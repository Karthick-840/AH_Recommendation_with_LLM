import os
import json
import yaml
import logging
from datetime import datetime

# Import core modules from the src directory
from src.get_bonus_items import get_all_bonus_items
# from src.check_products import filter_products_for_recommendation
# from src.llm_process import process_with_llm_and_generate_json
# from src.get_template_html import generate_product_email_html as json_to_html_generator
# from src.send_email import send_html_email_sendpulse

# Ensure data/outputs directory exists
ENABLE_FILE_LOGGING = True
LOG_FILE_NAME = 'app_logs.log'


def main():
    # Configure logging

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger("AHRecommendationApp")
    logger.setLevel(logging.DEBUG)

    logger.info("Starting AH Recommendation System Pipeline...")

    # Load configuration
    try:
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
        logger.info("Configuration loaded successfully.")
    except FileNotFoundError:
        logger.error(
            "Error: config.yml not found. Please create it as per the README.")
        return
    except Exception as e:
        logger.error(f"Error loading config.yml: {e}")
        return

    # # --- Step 1: Get Bonus Items ---
    # logger.info("Step 1: Getting daily bonus items...")
    # try:
    #     raw_bonus_items = get_all_bonus_items(config=config)
    #     if not raw_bonus_items:
    #         logger.warning("No raw bonus items retrieved. Exiting.")
    #         return
    #     logger.info(f"Retrieved {len(raw_bonus_items)} raw bonus items.")
    # except Exception as e:
    #     logger.error(f"Error in getting daily bonus items: {e}")
    #     return

    # # --- Step 2: Filter Products and Process with LLM for Recipes ---
    # logging.info(
    #     "Step 2: Filtering products and processing with LLM for recipes...")
    # try:
    #     # Filter products first
    #     filtered_products = filter_products_for_recommendation(
    #         raw_bonus_items, config, output_directory=OUTPUT_JSON_DIR)
    #     if not filtered_products:
    #         logging.warning("No products passed the filtering stage. Exiting.")
    #         return
    #     logging.info(f"Filtered down to {len(filtered_products)} products.")

    #     # Process filtered products with LLM to get recipes and structured JSON
    #     current_date_str = datetime.now().strftime('%Y%m%d')
    #     output_json_filename = config['output_paths']['generated_recommendations_json'].format(
    #         date=current_date_str)
    #     output_json_path = os.path.join(OUTPUT_JSON_DIR, output_json_filename)

    #     final_recommendation_data = process_with_llm_and_generate_json(
    #         filtered_products,
    #         config,
    #         output_json_path
    #     )

    #     if not final_recommendation_data:
    #         logging.warning(
    #             "LLM processing did not yield any recommendations or recipes. Exiting.")
    #         return
    #     logging.info(
    #         f"LLM processing complete. Recommendations saved to {output_json_path}")

    # except Exception as e:
    #     logging.error(f"Error in LLM processing or product filtering: {e}")
    #     return

    # # --- Step 3: Generate HTML Email ---
    # logging.info(
    #     "Step 3: Generating HTML email content from processed JSON...")
    # try:
    #     # json_to_html_generator takes the path to the JSON file to read from
    #     html_output_path = config['email']['html_output_file']
    #     json_to_html_generator(output_json_path, html_output_path)
    #     logging.info(f"HTML email content saved to {html_output_path}")
    # except Exception as e:
    #     logging.error(f"Error in generating HTML email: {e}")
    #     return

    # # --- Step 4: Send Email (via SendPulse) ---
    # logging.info("Step 4: Sending email...")
    # try:
    #     sender_email = os.environ.get(config['email']['sender_email_env_var'])
    #     sender_name = config['email']['sender_name']
    #     receiver_email = os.environ.get(
    #         config['email']['receiver_email_env_var'])
    #     subject = f"{config['email']['subject_prefix']} Daily Recommendations - {datetime.now().strftime('%Y-%m-%d')}"

    #     api_id = os.environ.get(config['sendpulse']['api_id_env_var'])
    #     api_secret = os.environ.get(config['sendpulse']['api_secret_env_var'])

    #     send_html_email_sendpulse(
    #         sender_email=sender_email,
    #         sender_name=sender_name,
    #         receiver_email=receiver_email,
    #         subject=subject,
    #         html_content_file=html_output_path,
    #         api_id=api_id,
    #         api_secret=api_secret
    #     )
    #     logging.info("Email sending process initiated.")
    # except Exception as e:
    #     logging.error(f"Error in sending email: {e}")
    #     return

    # logging.info("AH Recommendation System Pipeline finished successfully.")


if __name__ == "__main__":
    main()
