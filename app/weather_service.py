import requests
from typing import Dict, Any, Tuple
from app.config import NWS_USER_AGENT
from app.logger import get_logger

logger = get_logger(__name__)

class weatherService:
    base_url = 'https://api.weather.gov'
    HEADERS = {
    "User-Agent": NWS_USER_AGENT,
    "Accept": "application/ld+json"
}


    @staticmethod
    def get_gridpoint(lat: float, lon: float) -> Dict[str, Any]:
        
        logger.info(f"Fetching gridpoint for lat = {lat} and lon = {lon}")

        url = f"{weatherService.base_url}/points/{lat},{lon}"
        r = requests.get(url, headers= weatherService.HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        

        forecast_url = data["forecast"]
        hourly_url = data["forecastHourly"]
        # properties = data.get("properties", {})
        # forecast_url = properties.get("forecast")
        # hourly_url = properties.get("forecastHourly")
        logger.info("Received forecast urls")
        # forecast_lat = data['geometry'][1]
        # forecast_lon = data['geometry'][0]

        if not forecast_url or not hourly_url:
            raise ValueError(f"Missing forecast URLs in response")
        
        # grid_lat, grid_lon = weatherService.calculate_grid_center(data)
        # logger.info(data)

        return {
            "forecast_url": forecast_url,
            "hourly_url": hourly_url,
            # "grid_center_lat": grid_lat,
            # "grid_center_lon": grid_lon
        }
    


    @staticmethod
    def calculate_grid_center(data: Dict[str, Any]) -> Tuple[float, float]:
        try:
            logger.info(data)
            # geometry = data.get("geometry",{})
            # coorinates = geometry.get("coordinates", [])

            # if not coorinates or not coorinates[0]:
            #     return 0.0, 0.0
            
            # polygon = coorinates[0]

            geometry_str = data.get("geometry", "")
            if not geometry_str or not geometry_str.startswith("POLYGON"):
                logger.warning("No valid polygon geometry found")
                return 0.0, 0.0
            coords_str = geometry_str.replace("POLYGON((", "").replace("))", "")

            coord_pairs = coords_str.split(",")

            lats = []
            lons = []

            for pair in coord_pairs[:-1]:
                lon, lat = pair.strip().split()
                lats.append(float(lat))
                lons.append(float(lon))

            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)

            logger.info(f"Calculated grid center:({center_lat:.4f}, {center_lon:.4f})")
            return center_lat, center_lon
        except Exception as e:
            logger.warning(f"Failed to calculate grid center: {e}")
            return 0.0, 0.0



    @staticmethod
    def get_forecast(forecast_url: str) ->Dict[str, Any]:
        
        logger.info(f"Fetching forecast from {forecast_url}")

        r = requests.get(forecast_url, headers=weatherService.HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        grid_lat, grid_lon = weatherService.calculate_grid_center(data)
        # logger.info(data)
        # validate
        if "periods" not in data:
            raise ValueError(f"No periods found in forecast response. Keys available: {list(data.keys())}")
        
        logger.info(f"Found {len(data['periods'])} forecast periods")
        return {
            "forecast_data":data,
            "grid_center_lat": grid_lat,
            "grid_center_lon": grid_lon
        }

    @staticmethod
    def get_hourly_forecast(hourly_url: str) ->Dict[str, Any]:

        logger.info(f"Fetching hourly forecast from {hourly_url}")

        r = requests.get(hourly_url, headers=weatherService.HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        # logger.info(data)

        if "properties" not in data or "periods" not in data["properties"]:
             ValueError(f"Invalid hourly forecast structure. Keys: {list(data.keys())}")
        
        logger.info(f"Found {len(data['properties']['periods'])} hourly periods")

        return data