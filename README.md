# NWS Data Microservice

A containerized FastAPI based microservice that pulls data from NWS API (hourly and current weather forecast), performs data enrichment and transformation, and persists processed data to PostgreSQL with relationship modeling.

## Key Features

- POST endpoint `/weather` accepts `user_id`, `latitude`, and `longitude`
- Fetches gridpoint and forecast data form NWS API
- Enriches hourly data with temperature ratio, wind conditions, distance from requested coordinates, and precipitation
- Persists data (Normalized) in PostgreSQL using SQLAlchemy 
- Containerized with Docker and managed via `docker-compose`
- Environment-based configuration using `.env`
- Unit and integration tests with `pytest`

## Architecture Overview

```
- [Architecture Diagram](./images/Arch.png)
```

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker + docker-compose
- Python 3.10
- HTTPie for API testing
- Pytest for unit/integration tests

## 📚 Documentation

- [Architecture Overview](./ARCHITECTURE.md)

## Database Schema

```sql
weather_requests [1 - 1] current_forecasts
weather_requests [1 - Many] hourly_forecasts

# Complete relationship modeling with foreign keys and JSON raw data storage
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Internet connection (for NWS API access)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd weather_service

# Create environment file
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 2. Start Services

```bash

# Start all services
docker-compose up --build
# You'll see: "Tables created" when ready
```



## Run Tests
```bash
# All tests
docker-compose run --rm app pytest

# Specific test categories
docker-compose run pytest -s tests/test_api.py -v           # Integration tests
docker-compose run pytest -s tests/test_utils.py -v         # Unit tests  
docker-compose run pytest -s tests/test_weather_service.py -v  # Service tests

## API Reference

### POST /weather
Process weather data request with enrichment and persistence.

**Request:**
```json
{
  "user_id": "string",       // Required: User identifier
  "latitude": 42.3601,       // Required: -90 to 90
  "longitude": -71.0589      // Required: -180 to 180
}
```

**Response:** See example above in Quick Start section.

**Error Responses:**
- `400 Bad Request`: Invalid coordinates or missing fields
- `500 Internal Server Error`: Service or database errors

### **GET /healthz**
Health check endpoint for monitoring and load balancers.

**Response:**
```json
{"status": "ok"}
```

## Data Enrichment Details

The service performs data enrichment

### 1. Temperature Ratio Analysis

```python
temperature_ratio = hourly_temperature / average_forecast_temperature
# Values > 1.0 indicate above-average temperatures for the period
```

### 2. Wind Speed Trend Detection

```python
wind_above_avg = current_wind_speed > daily_average_wind_speed
# Boolean indicator for wind conditions
```

### 3. Geographic Distance Calculations
```python
lat_distance_km = abs(user_latitude - forecast_grid_latitude) * 111.32
lon_distance_km = abs(user_longitude - forecast_grid_longitude) * 111.32 * cos(latitude)
# Precise distance measurements from forecast grid center
```

### 4. Precipitation Probability Trends
Raw precipitation probabilities from NWS are preserved and made available for trend analysis.

## Database Design

### Schema Design Principles
- **Normalization**: Proper 3NF design with relationships
- **Data Integrity**: Foreign key constraints and validations
- **Raw Data Preservation**: JSON storage for future analysis
- **Performance**: Strategic indexing on query patterns

### **Table Structure**

```sql
-- Core request tracking
weather_requests: id, user_id, latitude, longitude, created_at

-- Current conditions (1:1 relationship)
current_forecasts: id, request_id, summary, temperature, wind_speed, raw_data

-- Hourly data with enrichments (1:many relationship) 
hourly_forecasts: id, request_id, temperature, temperature_ratio, 
                  wind_above_avg, lat_distance, lon_distance, raw_data
```

## Docker Configuration

### **Services Architecture**
- **app**: FastAPI application with auto-reload for development
- **db**: PostgreSQL 15 with persistent volumes and health checks
- **Networking**: Internal Docker network with proper dependencies

### Production Considerations
- Health checks configured for orchestration
- Restart policies for reliability  
- Volume mounts for database persistence
- Environment-based configuration


## Troubleshooting

### Common Issues

**"Database connection failed"**

```bash
# Check if database is ready
docker-compose logs db
# Wait for "database system is ready to accept connections"
```

**"ImportError: circular import"**

```bash
# Ensure you're using app/ directory structure
# Check that all imports use app.module_name format
```

**"No forecast data available"**

```bash
# Verify coordinates are within US boundaries (NWS limitation)
# Check internet connectivity for API calls
# Review logs: docker-compose logs app
```

## Testing Strategy

### **Test Coverage**
- **Unit Tests**: Data enrichment algorithms, utility functions
- **Integration Tests**: Full API workflow with mocked external services
- **Service Tests**: Weather service with mocked HTTP responses

### **Test Data Strategy**
- **Realistic Coordinates**: Boston, MA (42.3601, -71.0589) for consistent testing
- **Mock Responses**: Based on actual NWS API response structures
- **Edge Cases**: Invalid coordinates, missing data, API failures

### **Running Specific Tests**
```bash
# Test specific functionality
pytest tests/test_utils.py::test_enrich_hourly_forecast_basic -v
```

## Project Structure 
```arduino
app/
├── main.py
├── models.py
├── database.py
├── weather_service.py
├── utils.py
├── config.py
└── logger.py

tests/
├── test_api.py
├── test_utils.py
└── test_weather_service.py
```

## Codding Standard
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public methods
- Maintain test coverage above 80%

## 📄 **License**

This project is licensed under the MIT License - see LICENSE file for details.
---