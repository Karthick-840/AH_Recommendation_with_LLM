import pandas as pd
import re
from io import StringIO

def extract_year(row):
    year_match_title = re.search(r'\b(19\d{2}|20\d{2})\b', row['Title'])
    year_match_explanation = re.search(r'\b(19\d{2}|20\d{2})\b', row['Explanation'])
    if year_match_title:
        return int(year_match_title.group(1))
    elif year_match_explanation:
        return int(year_match_explanation.group(1))
    return None

def create_formatted_date(row):
    month_day_match = re.search(r'(\w+) (\d+)', row['Date'])
    year = extract_year(row)
    if month_day_match and year:
        month = month_day_match.group(1)
        day = int(month_day_match.group(2))
        try:
            pd_date = pd.to_datetime(f'{year}-{month}-{day}', format='%Y-%B-%d', errors='raise')
            return pd_date.strftime('%d %B %Y')
        except ValueError:
            return None
    elif year:
        month_match_explanation = re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b', row['Explanation'], re.IGNORECASE)
        if month_match_explanation:
            month_name = month_match_explanation.group(1)
            try:
                # Default to the 1st of the month if only month and year are found
                pd_date = pd.to_datetime(f'{year}-{month_name}-01', format='%Y-%B-%d', errors='raise')
                return pd_date.strftime('%d %B %Y')
            except ValueError:
                return None
    return None
