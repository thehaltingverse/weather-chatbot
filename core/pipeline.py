# weatherChatbot/core/pipeline.py

def generate_weather_report(city: str) -> str:    
    # Load libraries 
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    from transformers import pipeline
    from dotenv import load_dotenv
    import os
    import requests
    import json
    from datetime import datetime, timedelta, date
    import time
    import pandas as pd
    import openai
    import pprint
    from llama_cpp import Llama
    from huggingface_hub import hf_hub_download
    from pathlib import Path
    import subprocess
    import sys
    from typing import List, Dict
    import praw
    
    # Load custom modules
    from .weather_sources import get_coordinates, get_weatherbit_forecast, get_open_meteo_forecast, safe_noaa_request, generate_past_10yr_ranges, find_nearest_station, get_noaa_data_for_range, get_noaa_10yr_historical
    from .wrangle import normalize_forecast, merge_forecasts, normalize_noaa_data, summarize_noaa_data, summarize_noaa_daily_climatology, format_news_data, format_reddit_posts_for_llm
    from .llm_prompting import create_chatgpt_prompt, query_openai, query_llm_with_fallback, persona, instructions, output_format
    from .news_sources import extract_city_state, get_weather_news, US_STATE_ABBR_TO_NAME
    from .social_media_sources import fetch_reddit_weather_posts
    
    # Load API keys
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / "env" / ".env"
    load_dotenv(dotenv_path=env_path)
    WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY")
    NOAA_TOKEN = os.getenv("NOAA_TOKEN")
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")
    REDDIT_SECRET = os.getenv("REDDIT_SECRET")
    REDDIT_ID = os.getenv("REDDIT_ID")

    # Initialize OpenAI endpoint
    client = openai.OpenAI(api_key=OPENAI_KEY)
    
    # Obtain and print lat/lon coordinates for selected city.
    lat, lon = get_coordinates(city)

    # Obtain Weatherbit forecast data
    weatherbit_data = get_weatherbit_forecast(lat, lon, WEATHERBIT_API_KEY)

    # Obtain Open-Meteo forecast data
    open_meteo_data = get_open_meteo_forecast(lat, lon)

    # Obtain NOAA historical data
    noaa_data, station_id = get_noaa_10yr_historical(lat, lon, NOAA_TOKEN)
    
    # Fetch news data
    news_data = get_weather_news(city,api_key=NEWSAPI_API_KEY, max_articles=3)

    # Fetch Reddit posts
    reddit_data = fetch_reddit_weather_posts(
        reddit_client_id=REDDIT_ID,
        reddit_client_secret=REDDIT_SECRET,
        reddit_user_agent="WeatherAnalysisBot/0.1 by OkHold2363",
        location=city,
        max_posts=10
        )

    # Normalize and merge forecast data
    forecast_df_merged = merge_forecasts(open_meteo_data, weatherbit_data, normalize_forecast)

    # Normalize historical data
    historical_df = normalize_noaa_data(noaa_data)

    # Summarize historical data
    summary_historical_df = summarize_noaa_data(historical_df)

    # Summarize daily historical data
    daily_historical_df = summarize_noaa_daily_climatology(historical_df)

    # Format news articles for LLM
    news_formatted = format_news_data(news_data)

    # Format social media posts for LLM
    reddit_post_formatted = format_reddit_posts_for_llm(reddit_data)

    # Create artifacts for prompt
    df1_str = forecast_df_merged.to_json(orient='records') 
    df2_str = summary_historical_df.to_json(orient='records')
    df3_str = daily_historical_df.to_json(orient='records')

    # Create prompt
    prompt = create_chatgpt_prompt(persona, instructions, output_format, city, lat, lon, station_id, news_formatted, reddit_post_formatted, df1_str, df2_str, df3_str)
    # Query llm - this works
    # response = query_openai(client, prompt)

    # Query llm - testing this
    response = query_llm_with_fallback(client=client, prompt=prompt, openai_key=OPENAI_KEY)

    return response