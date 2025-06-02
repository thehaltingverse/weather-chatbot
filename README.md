Here is a complete `README.md` tailored to your `weatherChatbot` project, including all necessary notes about excluded files and setup steps:

---

````markdown
# WeatherChatbot

A prototype CLI and FastAPI-based weather assistant that generates a natural language 7-day forecast by synthesizing data from multiple sources (NOAA, Open Meteo, Weatherbit) and comparing it with 10-year historical weather data. An LLM (local or OpenAI) is used to summarize, resolve conflicts, and provide safety caveats.

---

## 🚀 Features

- 📍 Conversational CLI to collect and validate U.S. location input
- 🌦️ Aggregates forecast data from 3 sources
- 📊 Compares forecasts with 10-year NOAA historical data
- 🧠 LLM summarization: generates coherent forecast, resolves source conflicts
- 🛡️ Adds safety guidance when needed (e.g., storms, extreme heat)
- ⚙️ FastAPI backend for weather synthesis and data flow
- 🧪 Includes a working notebook for quick experimentation

---

## ⚠️ Setup Notes

This repository intentionally **excludes** some files due to security or size:

- `.env` – **NOT INCLUDED**  
  Add your API key manually:
  ```env
  OPENAI_KEY=your-openai-key
````

* `.venv/` – **NOT INCLUDED**
  Create your virtual environment locally:

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # or .venv\Scripts\activate on Windows
  pip install -r env/requirements.txt
  ```

* `.gguf` model files – **NOT INCLUDED**
  If using a local LLM like `OpenChat-3.5`, download a GGUF file (e.g., from Hugging Face) and place it in:

  ```
  models/
  ```

---

## 🛠️ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/weatherChatbot.git
cd weatherChatbot
python -m venv .venv
source .venv/bin/activate
pip install -r env/requirements.txt
```

### 2. Add Environment File

```bash
touch env/.env
# Paste your OpenAI key inside
```

### 3. Run CLI Assistant

```bash
python cli_agent/interactive_location_chat.py
```

### 4. Run FastAPI Server

```bash
uvicorn mcp_server.router:app --reload
```

---

## 📁 Project Structure

```
weatherChatbot/
├── cli_agent/               # CLI-based input collection
├── core/                    # Weather processing, LLM prompting
├── mcp_server/              # FastAPI router and dependencies
├── notebooks/               # Experiments and MVP dev
├── env/                     # Environment config and requirements
│   ├── .env                 # <- create manually
│   ├── requirements.txt
├── models/                  # <- download GGUF model manually
├── .venv/                   # <- create manually
├── .gitignore
├── README.md
```

---

## 🧠 LLM Options

This system supports either:

* **OpenAI API**: requires `OPENAI_KEY`
* **Local GGUF model**: if configured, used as fallback

---

## ✅ License

MIT (or your preferred license)

---

## 🙋‍♂️ Questions?

Contact the original author or raise an issue in the repo.