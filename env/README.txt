weatherChatbot/
├── cli_agent/
│   ├── main.py: Entry point for the command-line interface chatbot. Sends user input (e.g., city name) to the FastAPI server and displays the weather report.
│   ├── main-enhanced.py: Entry point for the command-line interface chatbot, this time with an LLM backend. Sends user input (e.g., city name) to the FastAPI server and displays the weather report.
│   ├── interactive_location_chat.py: Handles the LLM-enhanced CLI agent logic, setting boundary conditions, persona, and goals of conversation. Has failover to local LLM, but recommend to use OpenAI endpoint instead.
├── core/
│   ├── llm_prompting.py: Contains functions for constructing and formatting prompts to send to the LLM for generating human-readable forecasts and commentary.
│   ├── news_sources.py: Handles integration with external news APIs (NewsAPI) to retrieve relevant news data.
│   ├── pipeline.py: Orchestrates the full data flow: retrieving forecast and historical weather data, synthesizing it, and calling the LLM to produce final output.
│   ├── social_media_sources.py: Handles integration with external social media APIs (Reddit) to retrieve relevant social media data.
│   ├── weather_sources.py: Handles integration with external weather APIs (Open Meteo, Weatherbit, etc.) to retrieve 7-day forecast data.
│   ├── wrangle.py: Cleans, aligns, and transforms weather data from multiple sources and historical records into a consistent tabular format. Also contains functions to wrangle news and social media data and format for LLM consumption.
├── env/
│   ├── .env: Stores environment variables such as API keys and configuration flags for local development.
│   ├── README.txt: Briefly describes the important files used in this project. Does not include files that are implicitly required or automatically generated with the running of the pipeline.
│   ├── requirements.txt: Lists all Python dependencies required to run the project. Ensure that your execution environment has these packagkes.
├── mcp_server/
│   ├── dependencies.py: Contains reusable FastAPI dependency functions (e.g., for shared configurations, environment loading, or API client initialization).
│   ├── main.py: Initializes and runs the FastAPI server, exposing endpoints for weather forecasting.
│   ├── router.py: Defines the /forecast POST endpoint, which receives a city name and returns the generated weather forecast.
├── models/
│   ├── openchat-3.5-1210.Q4_K_M.gguf: Quantized local LLM model in GGUF format used for inference (e.g., generating commentary from structured weather data).
├── notebooks/
│   ├── report-final.docx: Written report, includes details requested in original problem statement.
│   ├── weather_forecast-final.ipynb: Jupyter notebook used for prototyping and validating the full pipeline, from raw data ingestion to final LLM-generated output. Contains details for running the pipeline within the notebook and also through an MCP server + CLI interface.
│   ├── weather_forecast-final-backup.ipynb: Backup Jupyter notebook.
