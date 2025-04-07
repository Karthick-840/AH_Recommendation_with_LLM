from helpers.scrape_wikipedia import intiate_scrapping
from helpers.preprocess_data import create_formatted_date,extract_year
import json
import pandas as pd
import re
from io import StringIO

# Main execution block
if __name__ == "__main__":
    WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_accidents_and_incidents_involving_commercial_aircraft'

    print("--- Starting Wikipedia Scraper ---")
    intiate_scrapping(WIKI_URL)
    print("--- Scraper Finished ---")

    df = pd.read_csv('data/raw_wikipedia_data.csv')
    df['Formatted_Date'] = df.apply(create_formatted_date, axis=1)
    df = df[['Formatted_Date','Date','Title','Explanation','Link']]
    df = df.sort_values(by='Formatted_Date')
    print(df)
    df.to_csv('data/preprocessed_data.csv')