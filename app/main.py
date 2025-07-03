from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.weather_service import weatherService
from app.utils import enrich_hourly_forecast, parse_wind
from app.logger import get_logger
from app.models import WeatherRequest, CurrentForecast, HourlyForecast
from dateutil.parser import isoparse
import time
from sqlalchemy.exc import OperationalError
from fastapi.responses import JSONResponse
from sqlalchemy import text


logger = get_logger(__name__)

MAX_RETIRES = 10
WAIT_TIME = 2

for i in range(MAX_RETIRES):
    try:
        # pass
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created")
        break

    except OperationalError as e:
        logger.error(f"DB Connection failed. Attempt {i+1} of {MAX_RETIRES}. Retrying in {WAIT_TIME}s ..")
        time.sleep(WAIT_TIME)



app = FastAPI()


class WeatherRequestInput(BaseModel):
    user_id: str
    latitude: float
    longitude: float



@app.get("/healthz")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        logger.exception("Health check failed: DB unreachable")
        return JSONResponse(status_code=500, content={"status": "db_unreachable"})

@app.post("/weather")
async def get_weather(data: WeatherRequestInput, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received request for user: {data.user_id} at ({data.latitude}, {data.longitude})")

        grid_data = weatherService.get_gridpoint(data.latitude, data.longitude)
        logger.info("Gridpoint pulled ... ")

        forecast = weatherService.get_forecast(grid_data['forecast_url'])
        grid_lat = forecast["grid_center_lat"]
        grid_lon = forecast["grid_center_lon"]

        hourly = weatherService.get_hourly_forecast(grid_data['hourly_url'])
        logger.info("Forecast and hourly data pulled ... ")

        # Inserting WeatherRequest
        request_entry = WeatherRequest(
            user_id=data.user_id,
            latitude=data.latitude,
            longitude=data.longitude
        )
        db.add(request_entry)
        db.flush()

        # Inserting CurrentForecast
        # current = forecast["periods"][0]
        # current = forecast.get("properties", {}).get("periods", [])[0]
        # current = forecast["properties"]["periods"][0]
        # current_periods = forecast.get("periods", [])
        current_periods = forecast["forecast_data"].get("periods", [])
        if not current_periods:
            raise ValueError("No current forecast period available")
        current = current_periods[0]
        current_entry = CurrentForecast(
            request_id=request_entry.id,
            summary=current.get("detailedForecast"),
            start_time=isoparse(current["startTime"]),
            temperature=current.get("temperature"),
            wind_speed=parse_wind(current.get("windSpeed", "0 mph")),
            precipitation_probability=current.get("probabilityOfPrecipitation", {}).get("value"),
            raw_data=current
        )

        db.add(current_entry)

        # Enrich and inserting HourlyForecast
        hourly_periods = hourly.get("properties", {}).get("periods", [])
        if not hourly_periods:
            raise ValueError("No hourly forecast period available")
        
        enriched = enrich_hourly_forecast(
            # hourly_periods=hourly["properties"]["periods"],
            hourly_periods=hourly_periods,
            original_lat=data.latitude,
            original_lon=data.longitude,
            forecast_lat=grid_lat,
            forecast_lon=grid_lon
        )

        for record in enriched:
            hourly_entry = HourlyForecast(
                request_id=request_entry.id,
                start_time=isoparse(record["startTime"]),
                temperature=record["temperature"],
                temperature_ratio=record["temperature_ratio"],
                wind_speed=record["wind_speed"],
                wind_above_avg=record["wind_above_avg"],
                precipitation_probability=record["precipitation_probability"],
                distance_miles=record["distance_miles"],
                raw_data=record
            )
            db.add(hourly_entry)

        db.commit()
        logger.info(f"Inserted 1 current and {len(enriched)} hourly records for request_id={request_entry.id}")

        return {
            "request_id": request_entry.id,
            "forecast_summary": current_entry.summary,
            "hourly_count": len(enriched)
        }

    except Exception:
        logger.exception('Error during weather request')
        # print(f'Error: {e}')
        return {"error": "Internal server error"}
