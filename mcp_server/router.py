# weatherChatbot/mcp_server/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from core.pipeline import generate_weather_report  # make sure this function exists

router = APIRouter()

class ForecastRequest(BaseModel):
    city: str

@router.post("/forecast")
def get_forecast(request: ForecastRequest):
    result = generate_weather_report(request.city)
    return {"city": request.city, "forecast": result}
