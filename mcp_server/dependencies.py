# mcp_server/dependencies.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Construct the path to env/.env relative to this file
env_path = Path(__file__).resolve().parents[1] / "env" / ".env"
load_dotenv(dotenv_path=env_path)

# Load the API keys
OPENAI_KEY = os.getenv("OPENAI_KEY")
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY")
NOAA_TOKEN = os.getenv("NOAA_TOKEN")