## 1. Overview
 A containerized **FastAPI** based microservice that pulls data from **NWS API** (hourly and current weather forecast), performs **data enrichment and transformation**, and **persists** processed data to **PostgreSQL** with relationship modeling
 ---
## 2.  Core Components
### 2.1 Fast API Application
- Serves as the main API interface.
- Exposes:
    - `POST /weather`: Ingests forecast request and processes data.
    - `GET /healthz`: Health check for monitoring and orchestration.
### 2.1 Weather Service
- Module (`weather_service.py`) responsible for:    
    - Calling NWS API endpoints:
        - `/points/{lat},{lon}`: Determines gridpoint metadata.
        - Forecast & hourly forecast URLs from gridpoint response.
    - Parsing and validating NWS responses.
    - Calculating grid center
### 2.3 Enrichment Logic 
- Function (`enrich_hourly_forecast`) that
    - Adds value to raw NWS data:
        1) Temperature ratio
        2) Wind trend detection
        3) Geographic distance between request and forecast grid
		4) Precipitation analysis

### 2.4 Database (Postgres)
 - Normalized schema with 3 tables:
    - `weather_requests`: User + location + timestamp
    - `current_forecasts`: 1:1 with request
    - `hourly_forecasts`: 1:Many with request
- Preserves raw API responses for traceability
- Indexed and foreign-keyed for performance and integrity

### 2.5 Logger
- Central logging configuration via `logger.py`
- Environment-based logging level from `.env`



## 3. Data Flow
1. **Client POSTs** request to `/weather` with `user_id`, `latitude`, `longitude`
2. **WeatherService** retrieves:
    - Gridpoint metadata        
    - Forecast + hourly data
3. **Enrichment** logic processes hourly records
4. **All data is saved** to PostgreSQL:
    - WeatherRequest → `weather_requests`
    - Current → `current_forecasts`
    - Hourly → `hourly_forecasts`
5. **Response returned** with summary and count
    
## 4. Testing Strategy
- Logic-level functions:
    - Enrichment calculations
    - Wind parsing
    - Grid geometry parsing
### 4.2. **Integration Tests**
- Full `/weather` workflow with mocked NWS responses
### 4.3. **Service Tests**
- Weather service layer methods via patched `requests.get`
### 4.4. **Test Tools**
- `pytest`, `unittest.mock`
- `TestClient` from FastAPI
## 5.  Deployment & Environment
### 5.1. **Docker + Docker Compose**
- `app`: FastAPI app container with Uvicorn
- `db`: PostgreSQL 15 with mounted volume 
- `depends_on` and health checks for sequencing
### 5.2. **Environment Support**
- `.env` file allows configuration overrides for:
    - Development
    - Staging
    - Production (with secure secrets handling)
## 6.  Observability & Reliability
- `/healthz` route provides basic DB connectivity check
- Logs all key stages (requests, API calls, DB writes)
- Resilient DB startup with retry mechanism
- Exceptions captured and logged with context
## 7. Security(Future Considerations)
- Input validation via Pydantic (already in use)
- AuthN/AuthZ not yet implemented (could add OAuth2 or API key)
- Secure `.env` management via vault/secrets manager
- HTTPS termination (currently HTTP only in local dev)
## 8. Extensibility Roadmap
- Add support for other weather APIs (fallback or enrichment)
- Scheduled jobs for periodic data pulls
- API documentation via OpenAPI/Swagger (already partially built-in with FastAPI)
- Metrics and alerting with Prometheus/Grafana