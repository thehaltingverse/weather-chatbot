# weatherChatbot/core/llm_prompting.py


persona = "You are a professional, friendly meteorologist, communicating with an audience about their local weather."
instructions = """
        First, analyze the provided table of weather forecast data for the city in question. It has the data from multiple sources. Use your expertise and knowledge about the weather for that location to provide a single, 7-day forecast of the weather in a table format along with any helpful commentary. For example, in cases where there is a large discrepancy between the two provided forecasts for a particular variable, consider providing commentary on its presence, potential root cause, and how you resolved it for the final forecast.
        Second, analyze and compare the summary historical data for the particular variable with the forecast data. 
        Third, analyze and compare the daily historical data for the particular variable on that date with the forecast data.
        For the second and third tasks, Consider including anything noteworthy in the "Historical comparison" section, for example calling out large deviations for historical data. Use your well-informed, and expert opinion to decide when and how to highlight discrepancies. Is the forecast typical compared to history? Anything unusual? Look at different metrics like temperature, humidity, wind, wind chill, cloud cover, etc.
        Fourth, for all of the weather variables, highlight important considerations that residents should take with regard to that variable including potential severe weather, unusual conditions, or impacts on daily life in the "Important considerations" section. For example, if there is extreme or unsafe temperatures, include a note to not leave children in cars, think about pets, and hydrate often.
        Fifth, in the "About the data" section, list any data anomalies, limitations, or special considerations that had to be taken into account in your analysis (for example, averaging two different values for temperature). Also attribute the sources of your data here.
        Sixth, the "Weather-related news" section: summarize the sentiment of the news articles that were found. Filter for only the most relevant to the weather and input location. Provide up to three high-quality news articles for reference.
        Seventh, the "Social media posts" section: summarize the sentiment of the social media posts that were found. Filter for only the most relevant to the weather and input location. Provide up to three high-relevancy posts for reference.
        If any data are conflicting or missing, please highlight and explain. If you are unsure of a conclusion, feel free to make it if you provide acknowledgement of limitations. If you don't know the answer, do not make one up or hallucinate a response; instead, acknowledge limitation(s) and recommend other actions to resolve. End your response politely and professionally.
        """
output_format = """The final 7-day forecast should be formatted as a table. The table should have the forecast the date along the top of the table, and the rows should contain the predicted value for the particular variable.

Example table:
| Date                | 2025-05-28 | 2025-05-29 | 2025-05-30 | 2025-05-31 | 2025-06-01 | 2025-06-02 | 2025-06-03 |
|---------------------|------------|------------|------------|------------|------------|------------|------------|
| Max Temp (°C)       | 39.0       | 37.3       | 38.9       | 39.1       | 33.2       | 35.0       | 33.2       |
| Min Temp (°C)       | 22.7       | 22.3       | 22.9       | 27.4       | 24.9       | 22.4       | 24.0       |
| Precipitation (mm)  | 0.0        | 0.0        | 0.0        | 0.25       | 2.5        | 2.5        | 0.0        |
| Max Wind Speed (m/s)| 8.9        | 7.3        | 10.0       | 17.4       | 18.6       | 18.5       | 15.6       |

Below the table, include a commentary section, formatted as below with the following information:

Commentary:
**Historical comparison:**
- individual points in bulleted list.

**Important considerations:**
- individual points in bulleted list.

**About the data:**
- individual points in bulleted list.

**Weather-related news:**
- Short summary of sentiment of recent weather-related news.
- Three relevant news articles, if present.

**Social media posts:**
- Short summary of sentiment of recent social media posts.
- Three relevant social media posts, including title and URL.
"""



def create_chatgpt_prompt(
    persona: str,
    instructions: str,
    output_format: str,
    city: str,
    lat: str,
    lon: str,
    station_id: str,
    news_formatted,
    reddit_post_formatted,
    df1_str: str,
    df2_str: str,
    df3_str: str
) -> str:
    """
    Construct a structured prompt for ChatGPT, embedding assistant persona, 
    task instructions, expected output format, and weather data context.

    Args:
        persona (str): Role and tone of the assistant (e.g., "a helpful meteorologist").
        instructions (str): Specific tasks for the assistant to complete.
        output_format (str): Target structure or formatting for the output.
        city (str): Name of the city for which the forecast is generated.
        lat (str): Latitude of the location.
        lon (str): Longitude of the location.
        station_id (str): NOAA station identifier.
        df1_str (str): Serialized forecast data (e.g., JSON or CSV) from source 1.
        df2_str (str): Serialized forecast data from source 2.
        df3_str (str): Serialized historical or climatology data.

    Returns:
        str: Fully formatted prompt string for use with the ChatGPT API.
    """
    prompt = f"""
                You are {persona}.

                Your task is to:
                {instructions}

                Here are the datasets to assist your analysis:

                Dataset 1:
                {df1_str}

                Dataset 2:
                {df2_str}

                Dataset 3:
                {df3_str}

                Please provide your response strictly following this format:

                City: {city}
                Latitude: {lat}
                Longitude: {lon}
                NOAA Station ID: {station_id}

                {output_format}

                """
    return prompt

def query_openai(client, prompt, model="gpt-4o", temperature=0.7, max_tokens=1000):
    """
    Send a prompt to the OpenAI ChatCompletion API and return the response.

    Args:
        client: Authenticated OpenAI API client instance.
        prompt (str): Text prompt to send to the LLM.
        model (str): Model name to use (default: "gpt-4o").
        temperature (float): Controls randomness of response; higher values yield more creative output.
        max_tokens (int): Maximum number of tokens to generate in the response.

    Returns:
        str: Text content of the LLM response, or an error message if the query fails.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def query_llm_with_fallback(
    client, 
    prompt: str,
    openai_key: str = None,
    notebook_path: str = None,
    repo_id: str = "TheBloke/OpenChat-3.5-1210-GGUF",
    model_filename: str = "openchat-3.5-1210.Q4_K_M.gguf",
    max_tokens: int = 1500,
    n_ctx: int = 8192,
    n_threads: int = 8,
    verbose: bool = False,
) -> str:
    """
    Query an OpenAI model if an API key is available; otherwise, fallback to a local GGUF model 
    (e.g., LLaMA-based) downloaded from Hugging Face.

    This function enables offline or budget-friendly inference by automatically switching 
    to a locally hosted quantized model if OpenAI credentials are not provided.

    Args:
        client: Authenticated OpenAI API client instance (used only if `openai_key` is provided).
        prompt (str): The prompt text to send to the language model.
        openai_key (str, optional): OpenAI API key. If None, the local model is used.
        notebook_path (Path, optional): Path to the current notebook or script. Used to resolve the model directory.
        repo_id (str): Hugging Face repository ID for downloading the GGUF model.
        model_filename (str): Filename of the GGUF model to load locally.
        max_tokens (int): Maximum tokens to generate in the response.
        n_ctx (int): Context window size for the local LLM.
        n_threads (int): Number of CPU threads used by the local model.
        verbose (bool): Whether to print verbose logs from the local model.

    Returns:
        str: The generated response text from the selected LLM backend.
    """
    from pathlib import Path
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama
    
    print("openai key",openai_key)
    
    if openai_key:
        print("Querying OpenAI endpoint...")
        response = query_openai(client, prompt)
        return response
    
    print("No OpenAI key detected. Using local GGUF model.")

    # Determine model directory relative to the notebook
    notebook_dir = notebook_path.parent if notebook_path else Path.cwd()
    local_model_dir = notebook_dir / "models"
    model_path = local_model_dir / model_filename

    # Download model if not present
    if not model_path.exists():
        print(f"Model not found locally. Downloading from Hugging Face...")
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=model_filename,
            local_dir=local_model_dir
        )
        print(f"Download complete. Model saved at: {model_path}")
    else:
        print(f"Using cached model at: {model_path}")

    # Initialize model
    print("Querying model, this may take some time...")
    llm = Llama(
        model_path=str(model_path),
        n_ctx=n_ctx,
        n_threads=n_threads,
        use_mlock=True,
        verbose=verbose
    )

    # Query model
    output = llm(prompt, max_tokens=max_tokens, echo=False)
    return output["choices"][0]["text"]