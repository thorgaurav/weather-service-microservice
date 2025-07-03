import pytest
from unittest.mock import patch, Mock
from app.weather_service import weatherService
import os
from dotenv import load_dotenv

load_dotenv()

@patch('app.weather_service.requests.get')
def test_get_gridpoint(mock_get):
    mock_response = Mock()
    mock_response.status == 200
    mock_response.json.return_value = {
        "forecast":"https://api.weather.gov/forecast/mock",
        "forecastHourly":"https://api.weather.gov/forecast/hourly/mock"
    }
    mock_get.return_value = mock_response

    result = weatherService.get_gridpoint(42.36, -71.05)
    assert "forecast_url" in result
    assert "hourly_url" in result

@patch("app.weather_service.requests.get")
def test_get_forecast(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "properties":{
            "periods":[{"detailedForecast":"Sunny"}]
        }
    }

    mock_get.return_value = mock_response

    forecast = weatherService.get_forecast("https://mockurl.gov/forecast")
    assert "periods" in forecast["properties"]


@patch("app.weather_service.requests.get")
def test_get_hourly_forecast(mock_get):
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "properties":{"periods" : [{"temperature": 75}]}
    }

    mock_get.return_value = mock_response

    hourly = weatherService.get_hourly_forecast("https://mockurl.gov/hourly")

    assert "periods" in hourly["properties"]

