from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

url = 'https://en.wikipedia.org/wiki/List_of_accidents_and_incidents_involving_commercial_aircraft'

try:
    page = requests.get(url)
except Exception as e:
    print('Error downloading page: ',e)
    
soup = BeautifulSoup(page.text, 'html.parser')

li_elements = soup.find_all('li')

# Initialize lists to store parsed data and those that don't follow the format
data = []
non_formatted = []

# Iterate through each <li> element
for li in li_elements:
    try:
        # Find the date (assuming it is at the start of the text)
        date_text = li.text.split('–')[0].strip()
        
        # Find the <a> tag (link) and its title
        a_tag = li.find('a')
        title = a_tag.get('title') if a_tag else 'No title'
        link = 'https://en.wikipedia.org' + a_tag.get('href') if a_tag else 'No link'

        # Find the explanation (everything after the title)
        explanation = li.text.split('–')[1].strip()

        # Append the data to the list as a tuple
        data.append([date_text, title, explanation, link])

    except Exception as e:
        # Append to non_formatted if any exception occurs (like not following the format)
        non_formatted.append(str(li))
        continue

# Create a DataFrame from the structured data
df = pd.DataFrame(data, columns=['Date', 'Title', 'Explanation', 'Link'])

# Save DataFrame as CSV
df.to_csv('formatted_data.csv', index=False)
print("DataFrame saved to formatted_data.csv")

# Save non-formatted elements as JSON
with open('unformatted_data.json', 'w') as f:
    json.dump(non_formatted, f, indent=4)
print("Unformatted data saved to unformatted_data.json")

# dfs = []
# for table in tables:
#     dfs.append(pd.read_html(str(table))[0])
    
# print(dfs)