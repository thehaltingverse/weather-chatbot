# Functions to manipulate data
import pandas as pd
import numpy as np
from typing import List, Dict


def normalize_forecast(data,source_name):
    """
    Normalize raw forecast data from a given source into a standardized DataFrame format.

    Args:
        data (dict): Raw forecast data from an API response.
        source_name (str): Name of the data source, e.g., "open_meteo" or "weatherbit".

    Returns:
        pd.DataFrame: Normalized DataFrame with date and standardized weather metrics.
    """
    normalized = []

    if source_name == "open_meteo":
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        for i, date in enumerate(dates):
            normalized.append({
                "date": date,
                "temp_max-degC-open_meteo": daily.get("temperature_2m_max", [None]*len(dates))[i],
                "temp_min-degC-open_meteo": daily.get("temperature_2m_min", [None]*len(dates))[i],
                "precip-mm-open_meteo": daily.get("precipitation_sum", [None]*len(dates))[i],
                "wind_max-mpersec-open_meteo": daily.get("windspeed_10m_max", [None]*len(dates))[i]
            })

    elif source_name == "weatherbit":
        for day in data.get("data", []):
            normalized.append({
                "date": day.get("datetime"),
                "temp_max-degC-weatherbit": day.get("max_temp"),
                "temp_min-degC-weatherbit": day.get("min_temp"),
                "precip-mm-weatherbit": day.get("precip"),
                "wind_max-mpersec-weatherbit": day.get("wind_spd")
            })

    return pd.DataFrame(normalized)

def merge_forecasts(open_meteo_data, weatherbit_data, normalize_fn):
    """
    Merge forecast data from multiple sources into a unified DataFrame.

    Args:
        open_meteo_data (dict): Raw forecast data from Open Meteo.
        weatherbit_data (dict): Raw forecast data from Weatherbit.
        normalize_fn (Callable): Function to normalize raw forecast data.

    Returns:
        pd.DataFrame: Merged DataFrame with columns from both sources joined on date.
    """
    # Normalize each source
    df_openmeteo = normalize_fn(open_meteo_data, source_name="open_meteo")
    df_weatherbit = normalize_fn(weatherbit_data, source_name="weatherbit")

    # Merge on date using outer join to retain all data points
    merged_df = pd.merge(df_openmeteo, df_weatherbit, on="date", how="outer")

    # Sort by date
    merged_df = merged_df.sort_values("date").reset_index(drop=True)
    
    return merged_df

def normalize_noaa_data(noaa_raw_data):
    """
    Normalize NOAA raw data into a standardized DataFrame.

    Args:
        noaa_raw_data (list of dict): List of daily NOAA measurements in raw form.

    Returns:
        pd.DataFrame: Normalized DataFrame with date and NOAA-compliant weather metrics:
            ['date', 'temp_max-degC-noaa', 'temp_min-degC-noaa',
             'precip-mm-noaa', 'wind_max-mpersec-noaa']
    """
    if not noaa_raw_data:
        return pd.DataFrame(columns=[
            "date",
            "temp_max-degC-noaa",
            "temp_min-degC-noaa",
            "precip-mm-noaa",
            "wind_max-mpersec-noaa"
        ])

    # Convert to DataFrame
    df = pd.DataFrame(noaa_raw_data)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    # Pivot so each datatype is a column
    df_pivot = df.pivot_table(index='date', 
                              columns='datatype', 
                              values='value', 
                              aggfunc='first').reset_index()

    # Rename columns with your naming convention
    df_pivot = df_pivot.rename(columns={
        "TMAX": "temp_max-degC-noaa",
        "TMIN": "temp_min-degC-noaa",
        "PRCP": "precip-mm-noaa",
        "AWND": "wind_max-mpersec-noaa"
    })

    # Ensure all columns exist
    expected_cols = [
        "date",
        "temp_max-degC-noaa",
        "temp_min-degC-noaa",
        "precip-mm-noaa",
        "wind_max-mpersec-noaa"
    ]
    for col in expected_cols:
        if col not in df_pivot.columns:
            df_pivot[col] = pd.NA

    # Reorder columns
    df_pivot = df_pivot[expected_cols]

    return df_pivot

def summarize_noaa_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics from NOAA historical weather data.

    Computes mean, standard deviation, and count for each weather metric.

    Args:
        df (pd.DataFrame): NOAA-normalized DataFrame with expected columns:
            'temp_max-degC-noaa', 'temp_min-degC-noaa',
            'precip-mm-noaa', 'wind_max-mpersec-noaa'

    Returns:
        pd.DataFrame: Summary table with rows for each variable and columns:
            ['mean', 'std', 'count']
    """
    # Ensure date is datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    # Define weather columns to summarize
    weather_cols = [
        "temp_max-degC-noaa",
        "temp_min-degC-noaa",
        "precip-mm-noaa",
        "wind_max-mpersec-noaa"
    ]

    # Drop rows where all weather columns are missing
    df_clean = df.dropna(subset=weather_cols, how="all")

    # Ensure all columns are numeric (e.g., convert <NA> to np.nan)
    for col in weather_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Create summary stats
    summary = pd.DataFrame({
        "mean": df_clean[weather_cols].mean(),
        "std": df_clean[weather_cols].std(),
        "count": df_clean[weather_cols].count()
    })

    # Round results for clarity
    summary = summary.round(2)

    return summary

def summarize_noaa_daily_climatology(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute climatological summaries for each day-of-year based on NOAA historical data.

    Groups weather observations by month-day to estimate average, standard deviation, 
    and count per day-of-year across years.

    Args:
        df (pd.DataFrame): NOAA-normalized DataFrame with columns:
            'date', 'temp_max-degC-noaa', 'temp_min-degC-noaa',
            'precip-mm-noaa', 'wind_max-mpersec-noaa'

    Returns:
        pd.DataFrame: Per-day-of-year summary DataFrame with columns like:
            'month_day', 'temp_max-degC-noaa-mean', ..., 'wind_max-mpersec-noaa-std'
    """
    # Ensure datetime format
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # Extract month and day to group by day-of-year
    df["month_day"] = df["date"].dt.strftime("%m-%d")

    # Define weather columns
    weather_cols = [
        "temp_max-degC-noaa",
        "temp_min-degC-noaa",
        "precip-mm-noaa",
        "wind_max-mpersec-noaa"
    ]

    # Ensure numeric and drop rows missing all variables
    df_clean = df.dropna(subset=weather_cols, how="all")
    for col in weather_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Group by month_day and calculate summary stats
    summary = df_clean.groupby("month_day")[weather_cols].agg(['mean', 'std', 'count'])

    # Flatten multi-index columns
    summary.columns = ['-'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()

    return summary

def format_news_data(articles: List[Dict]) -> str:
    """
    Formats a list of weather-related news articles into a readable summary
    suitable for LLM prompting or report inclusion.

    Args:
        articles (List[Dict]): A list of dictionaries, each containing metadata
                               for a news article with keys like 'title',
                               'source', 'datePublished', 'snippet', and 'url'.

    Returns:
        str: A formatted string summarizing article details. If no articles are
             provided, returns a fallback message.
    """
    if not articles:
        return "No weather-related news was found for this city in the past few days."

    lines = ["Recent Weather News Articles:"]
    for i, a in enumerate(articles, 1):
        title = a.get("title", "No Title")
        source = a.get("source", "Unknown Source")
        date = a.get("datePublished", "Unknown Date")
        snippet = a.get("snippet", "No snippet available.")
        url = a.get("url", "No URL")

        lines.append(
            f"\n[{i}] {title}\n"
            f"Source: {source} | Published: {date}\n"
            f"Snippet: {snippet}\n"
            f"Link: {url}"
        )
    return "\n".join(lines)

def format_reddit_posts_for_llm(posts: List[Dict]) -> str:
    """
    Format Reddit posts for input to an LLM.

    Args:
        posts (List[Dict]): List of Reddit post dicts with keys 'title', 'subreddit', 'created_utc', 'url', 'selftext'.

    Returns:
        str: Formatted multi-line string summarizing posts.
    """
    from datetime import datetime

    formatted_posts = []
    for post in posts:
        # Convert epoch UTC to readable datetime string
        dt = datetime.utcfromtimestamp(post['created_utc']).strftime('%Y-%m-%d %H:%M UTC')
        # Snippet from selftext, limit to 150 chars (or empty if no selftext)
        snippet = (post['selftext'][:150] + '...') if post['selftext'] else ''
        formatted = (
            f"[{dt}] r/{post['subreddit']}: {post['title']}\n"
            f"Snippet: {snippet}\n"
            f"URL: {post['url']}\n"
            "----"
        )
        formatted_posts.append(formatted)

    return "\n".join(formatted_posts)

