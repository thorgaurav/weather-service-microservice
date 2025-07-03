# tests/test_api.py

from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from datetime import datetime, timedelta

client = TestClient(app)

start = datetime(2025, 7, 3, 0, 0)

mock_forecast = {
        "forecast_data": {
        "periods": [
            {
                "startTime": "2025-07-03T06:00:00-04:00",
                "temperature": 75,
                "windSpeed": "5 mph",
                "detailedForecast": "Sunny",
                "probabilityOfPrecipitation": {"value": 20}
            }
        ]},
        "grid_center_lat": 42.3601,
        "grid_center_lon": -71.0589
    }

mock_hourly = {
    "properties": {
        "periods": [
            {
                "startTime": (start + timedelta(hours=i)).isoformat(),
                "temperature": 70 + i % 5,
                "windSpeed": "5 mph",
                "probabilityOfPrecipitation": {"value": 10 + i}
            }
            for i in range(24)
        ]
    }
}

mock_gridpoint = {
    "forecast_url": "https://api.weather.gov/gridpoints/BOX/71,90/forecast",
    "hourly_url": "https://api.weather.gov/gridpoints/BOX/71,90/forecast/hourly"
}


@patch("app.main.weatherService.get_hourly_forecast", return_value=mock_hourly)
@patch("app.main.weatherService.get_forecast", return_value=mock_forecast)
@patch("app.main.weatherService.get_gridpoint", return_value=mock_gridpoint)
def test_weather_endpoint(mock_grid, mock_forecast, mock_hourly):
    response = client.post("/weather", json={
        "user_id": "test_user",
        "latitude": 42.3601,
        "longitude": -71.0589
    })

    print("Response JSON:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "forecast_summary" in data
    assert "hourly_count" in data
    assert data["hourly_count"] == 24