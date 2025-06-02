# weatherChatbot/cli_agent/main.py

import requests
from rich.console import Console
from rich.markdown import Markdown
from interactive_location_chat import run_location_chat

def get_forecast(city: str):
    try:
        response = requests.post("http://127.0.0.1:8000/forecast", json={"city": city})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def main():
    console = Console()
    console.print("[bold green]MCP Weather CLI[/bold green]\n")

    # Step 1: Run the location chat
    location = run_location_chat()

    # Step 2: Exit if no valid location was obtained
    if not location:
        console.print("[bold red]No valid location provided. Exiting application.[/bold red]")
        return

    console.print(f"\n[bold blue]Generating weather forecast for:[/bold blue] {location}\n")

    # Step 3: Get forecast from MCP server
    forecast_data = get_forecast(location)

    # Step 4: Display forecast or error
    if "error" in forecast_data:
        console.print(f"[bold red]Error:[/bold red] {forecast_data['error']}")
    else:
        forecast_text = forecast_data.get("forecast", "")
        if isinstance(forecast_text, list):
            for day in forecast_text:
                console.print(day)
        else:
            console.print(Markdown(forecast_text))

if __name__ == "__main__":
    main()
