import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def intiate_scrapping(WIKI_URL):
    scraped_df, unformatted_list = scrape_wikipedia_list_items(WIKI_URL)

    OUTPUT_CSV = 'data/raw_wikipedia_data.csv'
    OUTPUT_JSON = 'data/inaccessible_webpage.json'

    # Check if the scraping returned data before saving
    if not scraped_df.empty:
        try:
            scraped_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
            print(f"Formatted data DataFrame saved to {OUTPUT_CSV}")
        except Exception as e:
            print(f"Error saving DataFrame to CSV: {e}")
    else:
        print("No formatted data scraped, CSV file not saved.")

    if unformatted_list:
        try:
            # Save non-formatted elements as JSON
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                 # Use ensure_ascii=False for proper UTF-8 output if needed
                json.dump(unformatted_list, f, indent=4, ensure_ascii=False)
            print(f"Unformatted <li> elements saved to {OUTPUT_JSON}")
        except Exception as e:
            print(f"Error saving unformatted data to JSON: {e}")
    else:
        print("No unformatted elements found or error during scraping.")

def scrape_wikipedia_list_items(url):
    
    print(f"Requesting page: {url}")
    try:
        page = requests.get(url, timeout=10) # Added timeout
        page.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        print("Page downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f'Error downloading page: {e}')
        # Return empty structures on failure
        return pd.DataFrame(columns=['Date', 'Title', 'Explanation', 'Link']), []

    soup = BeautifulSoup(page.text, 'html.parser')

    li_elements = soup.find_all('li')     # Target specific sections that gets data from each year
    print(f"Found {len(li_elements)} <li> elements.")

    # Initialize lists to store parsed data and those that don't follow the format
    data = []
    non_formatted_elements = []

    # Iterate through each <li> element
    for li in li_elements:
        # Attempt to parse based on the 'Date – Title Explanation' structure
        try:
            # Use the full text content of the list item
            full_text = li.get_text(separator=' ', strip=True) # Get text cleanly

            # Split based on the first '–' (en dash)
            parts = full_text.split('–', 1) # Split only once

            if len(parts) == 2:
                date_text = parts[0].strip()
                rest_of_text = parts[1].strip()

                # Find the first <a> tag within this <li> for title and link
                a_tag = li.find('a')
                if a_tag and a_tag.get('title'):
                    title = a_tag.get('title')
                    link = a_tag.get('href')
                    # Construct absolute URL if relative
                    if link and link.startswith('/'):
                        link = 'https://en.wikipedia.org' + link
                    elif not link:
                         link = 'No link found'

                    # Check if the title is part of the remaining text
                    # Explanation is tricky, might be better to take the full text after '–'
                    explanation = rest_of_text # Simplified assumption

                    # Append the data to the list
                    data.append([date_text, title, explanation, link])
                else:
                    # If no usable <a> tag found, mark as non-formatted
                    non_formatted_elements.append(str(li))
            else:
                 # If the split didn't yield two parts, mark as non-formatted
                 non_formatted_elements.append(str(li))

        except Exception as e:
            # Append to non_formatted if any unexpected exception occurs
            print(f"Error parsing li element: {e} - Element: {str(li)[:100]}...") # Log error
            non_formatted_elements.append(str(li))
            continue # Move to the next li element

    # Create a DataFrame from the structured data
    df = pd.DataFrame(data, columns=['Date', 'Title', 'Explanation', 'Link'])
    print(f"Successfully parsed {len(df)} elements into DataFrame.")

    return df, non_formatted_elements

