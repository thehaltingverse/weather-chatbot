# Functions to obtain news data

from typing import List, Dict
from datetime import datetime, timedelta, date
import requests

US_STATE_ABBR_TO_NAME = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
    'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
    'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
    'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
    'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia'
}

def extract_city_state(location: str) -> tuple[str, str]:
    """
    Extracts the city name and state name from a location string formatted as
    'City', 'City, State', or 'City, State, Country'. Converts US state abbreviations
    to full state names.

    Args:
        location (str): A location string, e.g., 'Phoenix, AZ' or 'Los Angeles, CA, USA'.

    Returns:
        tuple[str, str]: A tuple containing the extracted city name and full state name.
                         If no state is found, returns empty string for state.
                         Example: ('Phoenix', 'Arizona'), ('Los Angeles', 'California'), ('London', '')
    """
    if not location or not isinstance(location, str):
        return "", ""

    parts = [part.strip() for part in location.split(",") if part.strip()]
    city = parts[0] if len(parts) >= 1 else ""
    state = parts[1].upper() if len(parts) >= 2 else ""

    # Convert state abbreviation to full name if found
    full_state = US_STATE_ABBR_TO_NAME.get(state, parts[1] if len(parts) >= 2 else "")

    return city, full_state

def get_weather_news(city: str, api_key: str, days_back: int = 3, max_articles: int = 5) -> List[Dict]:
    """
    Queries the NewsAPI for weather-related news articles about a given city.

    Args:
        city (str): The city to search news for. Accepts formats like 'City, State'.
        api_key (str): Your NewsAPI.org API key.
        days_back (int): How many days back to search for news.
        max_articles (int): Maximum number of articles to return.

    Returns:
        List[str]: A list of formatted article summaries.
    """
    # Extract the city name to improve search relevance
    clean_city,clean_state = extract_city_state(city)
    print(clean_city, clean_state)
    
    # Build query
    # query = f"{clean_city} weather OR storm OR rainfall OR heat OR climate OR flood"
    
    query = (
        f"({clean_city} OR {clean_state})"
        "AND (weather OR storm OR forecast OR temperature OR rainfall OR snow OR flooding OR humidity) "
        "-sports -baseball -football -NBA -concert -game -soccer -crime"
    )

    # Dates
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": max_articles,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        return [
            {
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "datePublished": article.get("publishedAt"),
                "snippet": article.get("description"),
                "url": article.get("url")
            }
            for article in articles if article.get("title") and article.get("description")
        ]

    except Exception as e:
        print(f"[NewsAPI Error] {e}")
        return []
