from app.utils import enrich_hourly_forecast

def test_enrich_hourly_forecast_basic():
    mock_hourly_data = [{
          "startTime": "2025-07-01T10:00:00-04:00",
          "temperature": 70,
          "windSpeed": "10 mph",
          "probabilityOfPrecipitation": {"value": 20}
    },{
        "startTime": "2025-07-01T11:00:00-04:00",
        "temperature": 90,
        "windSpeed": "20 mph",
        "probabilityOfPrecipitation": {"value": 30}
    }]

    enriched = enrich_hourly_forecast(
        hourly_periods = mock_hourly_data,
        original_lat = 42.36,
        original_lon = -71.05,
        forecast_lat = 42.46,
        forecast_lon = -71.05
    )
        
    

    assert len(enriched) == 2

    for record in enriched:
        assert "temperature_ratio" in record
        assert "wind_speed" in record
        assert "precipitation_probability" in record
        assert record["lat_distance"] == 0.1
        assert record["lon_distance"] == 0.0