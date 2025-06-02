# weatherChatbot/cli_agent/main.py

import requests
from rich.console import Console
from rich.markdown import Markdown

def get_forecast(city: str):
    try:
        response = requests.post("http://127.0.0.1:8000/forecast", json={"city": city})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def main():
    console = Console()
    console.print("[bold green]MCP Weather CLI[/bold green]")

    while True:
        city = input("Enter a city (or 'q' to quit): ")
        if city.lower() == 'q':
            break

        forecast_data = get_forecast(city)

        if "error" in forecast_data:
            console.print(f"[bold red]Error:[/bold red] {forecast_data['error']}")
        else:
            forecast_text = forecast_data["forecast"]
            if isinstance(forecast_text, list):  # If you sent a list of dicts (e.g., DataFrame)
                for day in forecast_text:
                    console.print(day)
            else:  # If it's a string with markdown-like formatting
                console.print(Markdown(forecast_text))

if __name__ == "__main__":
    main()
