# core/weather_sources.py
import os
import time
import requests
from datetime import date, timedelta
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


def get_coordinates(city_name):
    """Get latitude and longitude for a given city name using Nominatim.

    Args:
        city_name (str): Name of the city to geocode.

    Returns:
        tuple: A tuple containing (latitude, longitude) as floats.
               Returns (None, None) if location is not found.
    """
    geolocator = Nominatim(user_agent="weather_forecast")
    location = geolocator.geocode(city_name)
    
    if not location:
        print(f"Location not found for city: {city_name}")
        return None, None
    
    lat, lon = location.latitude, location.longitude
    print(f"Coordinates for {city_name}: lat={lat}, lon={lon}")
    return lat, lon


def get_weatherbit_forecast(lat, lon, WEATHERBIT_API_KEY):
    """Fetch 7-day forecast from the Weatherbit API.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        WEATHERBIT_API_KEY (str): API key for Weatherbit.

    Returns:
        dict: JSON response from Weatherbit API if successful, empty dict otherwise.
    """
    url = "https://api.weatherbit.io/v2.0/forecast/daily"
    params = {
        "lat": lat,
        "lon": lon,
        "key": WEATHERBIT_API_KEY,
        "days": 7
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Weatherbit API error:", response.status_code)
        return {}


def get_open_meteo_forecast(lat, lon):
    """Fetch 7-day forecast from the Open-Meteo API.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        dict: JSON response from Open-Meteo API if successful, empty dict otherwise.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max"
        ],
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Open-Meteo API error:", response.status_code)
        return {}


def safe_noaa_request(url, headers, params, max_retries=5, backoff=5):
    """Perform a robust GET request to the NOAA API with retries on failure.

    Args:
        url (str): The NOAA API endpoint.
        headers (dict): Request headers.
        params (dict): Query parameters.
        max_retries (int): Maximum number of retry attempts.
        backoff (int): Initial backoff time in seconds between retries.

    Returns:
        requests.Response or None: The response object if successful, None otherwise.
    """
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response
        elif response.status_code == 503:
            print(f"503 error, retrying in {backoff} seconds...")
            time.sleep(backoff)
            backoff *= 2
        else:
            print(f"NOAA API error {response.status_code}: {response.text}")
            break
    return None


def generate_past_10yr_ranges(days_back=7):
    """Generate date ranges for the past 10 years for the same week period.

    Args:
        days_back (int): Number of days in each range (default is 7).

    Returns:
        list of tuple: A list of (start_date, end_date) pairs in 'YYYY-MM-DD' format.
    """
    today = date.today()
    ranges = []
    for i in range(1, 11):
        try:
            start = today.replace(year=today.year - i)
        except ValueError:
            start = today.replace(year=today.year - i, day=28)  # Handle Feb 29
        end = start + timedelta(days=days_back)
        ranges.append((start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))
    return ranges


def find_nearest_station(lat, lon, start_date, end_date,NOAA_TOKEN):
    """Find the nearest USW station with historical data coverage from NOAA.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        NOAA_TOKEN (str): NOAA API token.

    Returns:
        str or None: Station ID if found, otherwise None.
    """
    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/stations"
    headers = {"token": NOAA_TOKEN}
    params = {
        "datasetid": "GHCND",
        "startdate": start_date,
        "enddate": end_date,
        "limit": 1000,
        "extent": f"{lat - 1},{lon - 1},{lat + 1},{lon + 1}",
        "sortfield": "datacoverage",
        "sortorder": "desc"
    }
    response = safe_noaa_request(url, headers, params)
    if response and response.status_code == 200:
        stations = response.json().get("results", [])
        usw_stations = [s for s in stations if s["id"].startswith("GHCND:USW")]
        if not usw_stations:
            print("No USW stations found in bounding box.")
            return None
        closest_usw_station = min(
            usw_stations,
            key=lambda s: geodesic((lat, lon), (s["latitude"], s["longitude"])).km
        )
        print(f"Closest USW station: {closest_usw_station['id']} - {closest_usw_station.get('name', '')}")
        return closest_usw_station["id"]
    else:
        print(f"NOAA API request failed with status: {response.status_code if response else 'No response'}")
    return None


def get_noaa_data_for_range(station_id, start_date, end_date, NOAA_TOKEN, datatypeids=None):
    """Fetch NOAA weather data for a specific station and date range.

    Args:
        station_id (str): NOAA station ID.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        NOAA_TOKEN (str): NOAA API token.
        datatypeids (list, optional): List of NOAA data types. Defaults to ['TMIN', 'TMAX', 'PRCP', 'AWND'].

    Returns:
        list: A list of weather data records (dicts).
    """
    if datatypeids is None:
        datatypeids = ["TMIN", "TMAX", "PRCP", "AWND"]

    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": NOAA_TOKEN}
    all_results = []
    limit = 1000
    offset = 1

    while True:
        params = {
            "datasetid": "GHCND",
            "datatypeid": datatypeids,
            "stationid": station_id,
            "startdate": start_date,
            "enddate": end_date,
            "limit": limit,
            "offset": offset,
            "units": "standard",
            "sortfield": "date",
            "sortorder": "asc",
            "includemetadata": "false"
        }
        response = safe_noaa_request(url, headers, params)
        if not response:
            break
        data = response.json()
        results = data.get("results", [])
        all_results.extend(results)
        metadata = data.get("metadata", {}).get("resultset", {})
        count = metadata.get("count", 0)
        if offset + limit > count:
            break
        offset += limit

    return all_results


def get_noaa_10yr_historical(lat, lon, NOAA_TOKEN, days_back=7):
    """Get NOAA historical weather data for the past 10 years for a location.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        NOAA_TOKEN (str): NOAA API token.
        days_back (int): Number of days to fetch per year (default is 7).

    Returns:
        tuple: A tuple containing:
            - list of dicts: Combined weather data over 10 years.
            - str: Station ID used for data retrieval.

    Raises:
        ValueError: If no suitable station is found with data coverage.
    """
    date_ranges = generate_past_10yr_ranges(days_back)
    earliest_start, earliest_end = date_ranges[-1]
    station_id = find_nearest_station(lat, lon, earliest_start, earliest_end, NOAA_TOKEN)
    if not station_id:
        raise ValueError("No NOAA station found with data coverage for the location and date range.")

    print(f"Using station {station_id}")
    combined_results = []
    for start_date, end_date in date_ranges:
        print(f"Fetching data for {start_date} to {end_date}...")
        data = get_noaa_data_for_range(station_id, start_date, end_date, NOAA_TOKEN)
        combined_results.extend(data)

    return combined_results, station_id
