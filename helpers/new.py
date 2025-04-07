import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Example URL to scrape (replace with actual)
url = 'https://example.com'  # Replace with the actual URL

# Send a request and parse the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all <li> elements
li_elements = soup.find_all('li')

# Initialize lists to store parsed data and those that don't follow the format
data = []
non_formatted = []

# Iterate through each <li> element
for li in li_elements:
    try:
        # Extract the date - Assume it's before the first hyphen (-)
        parts = li.text.split('–')  # Split by the hyphen
        if len(parts) < 2:
            raise ValueError("Not enough parts after split")

        date_text = parts[0].strip()  # Date

        # Find the <a> tag (for title and link)
        a_tag = li.find('a')
        if a_tag:
            title = a_tag.get('title', 'No title')
            link = 'https://en.wikipedia.org' + a_tag.get('href')
        else:
            title = 'No title'
            link = 'No link'

        # Explanation is the remaining part after the hyphen
        explanation = parts[1].strip()

        # Append to the data list
        data.append([date_text, title, explanation, link])

    except Exception as e:
        # If parsing fails, save the whole li tag in unformatted list
        non_formatted.append({
            'html': str(li),  # Save the HTML of the li tag
            'error': str(e)   # Optional error message for debugging
        })

# Create a DataFrame from the structured data
df = pd.DataFrame(data, columns=['Date', 'Title', 'Explanation', 'Link'])

# Save DataFrame as CSV
df.to_csv('formatted_data.csv', index=False)
print("DataFrame saved to formatted_data.csv")

# Save non-formatted elements as JSON
with open('unformatted_data.json', 'w') as f:
    json.dump(non_formatted, f, indent=4)
print("Unformatted data saved to unformatted_data.json")
