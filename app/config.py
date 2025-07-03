import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://gp_user:gp_pass@localhost:5432/weather_db")
print("Loaded DB_URL:", DB_URL)
NWS_USER_AGENT = os.getenv("NWS_USER_AGENT", "globalP-weather-app (thorgaurav@gmail.com)")
LOG_LEVEL= os.getenv("LOG_LEVEL", "INFO")
