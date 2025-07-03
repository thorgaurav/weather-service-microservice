from typing import List, Dict
from geopy.distance import geodesic

def enrich_hourly_forecast(
        hourly_periods: List[Dict],
        original_lat: float,
        original_lon: float,
        forecast_lat: float,
        forecast_lon: float
)-> List[Dict]:
    enriched = []
    print("Enrichment started")
    # print(f"Raw hourly periods: {hourly_periods[:2]}")

    
    temperatures = [p["temperature"] for p in hourly_periods[:24] if p["temperature"] is not None]
    wind_speed = [p["windSpeed"] for p in hourly_periods[:24] if "windSpeed" in p and p["windSpeed"]]



    # wind_speed_numeric = [int(ws.split()[0]) if ws.split()[0].isdigit() else 0 for ws in wind_speed]
    wind_speed_numeric = [parse_wind(ws) for ws in wind_speed]

    avg_temp = sum(temperatures) / len(temperatures) if temperatures else 1
    avg_wind_speed = sum(wind_speed_numeric) / len(wind_speed_numeric) if wind_speed_numeric else 1


    user_coords = (original_lat, original_lon)
    grid_coords = (forecast_lat, forecast_lon)
    distance_miles = geodesic(user_coords, grid_coords).miles
    
    for p in hourly_periods[:24]:
        temp = p.get("temperature", 0)
        wind_str = p.get("windSpeed", "0 mph")
        wind_speed = parse_wind(wind_str)

        enriched.append({
            "startTime": p.get("startTime"),
            "temperature": temp,
            "temperature_ratio": round(temp / avg_temp, 2) if avg_temp else None,
            "wind_speed": wind_speed,
            "wind_above_avg":wind_speed > avg_wind_speed,
            "precipitation_probability": p.get("probabilityOfPrecipitation", {}).get("value"),
            "distance_miles": round(distance_miles, 4)
        })
    return enriched

def parse_wind(wind_str: str) -> int:
    """
    Extracts wind speed number from the string
    """
    try:
        return int(wind_str.split()[0])
    except:
        return 0

