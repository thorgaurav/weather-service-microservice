# app/models.py

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, JSON
from app.database import Base
from sqlalchemy.orm import Session, relationship
from datetime import datetime
from app.logger import get_logger

logger = get_logger(__name__)


class WeatherRequest(Base):
    __tablename__ = "weather_requests"
    id = Column(Integer, primary_key = True)
    user_id = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default = datetime.utcnow)
    current = relationship("CurrentForecast", back_populates = "request", uselist = False)
    hourly = relationship("HourlyForecast", back_populates = "request")


class CurrentForecast(Base):
    __tablename__ = "current_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("weather_requests.id"), nullable=False)
    summary = Column(String)
    start_time = Column(DateTime)
    temperature = Column(Float)
    wind_speed = Column(Float)
    precipitation_probability = Column(Float)
    raw_data = Column(JSON)
    request = relationship("WeatherRequest", back_populates="current")

class HourlyForecast(Base):
    __tablename__ = "hourly_forecasts"
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("weather_requests.id"), nullable=False)
    start_time = Column(DateTime)
    temperature = Column(Float)
    temperature_ratio = Column(Float)
    wind_speed = Column(Float)
    wind_above_avg = Column(Boolean)
    precipitation_probability = Column(Float)
    distance_miles = Column(Float)
    raw_data = Column(JSON)
    request = relationship("WeatherRequest", back_populates="hourly")
