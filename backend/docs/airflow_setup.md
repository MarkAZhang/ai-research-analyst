# Airflow Setup for REST API Access

This document explains how to configure Apache Airflow 3.x to work with the Django application via the REST API.

## Configuration

The AirflowClient in `backend/core/airflow_client.py` uses the Airflow REST API (v2) with JWT token authentication to trigger DAGs from Django.

## Authentication Flow

The client uses JWT tokens for authentication with Airflow's Simple Auth Manager:

1. **Token Generation**: The client fetches a JWT token from `/auth/token` using username/password
2. **Token Usage**: The token is included in the `Authorization: Bearer <token>` header for API requests
3. **Automatic Refresh**: If a 401 error is encountered, the client automatically refreshes the token and retries

No additional Airflow configuration is required - the Simple Auth Manager is enabled by default in Airflow 3.x.

## Testing the REST API

You can test the REST API using curl:

```bash
# Get a JWT token
TOKEN=$(curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}' \
  http://localhost:8080/auth/token | jq -r '.access_token')

# List DAGs
curl -X GET \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/v2/dags

# Trigger a DAG
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conf": {"report_id": 1}, "logical_date": "2025-01-01T00:00:00Z"}' \
  http://localhost:8080/api/v2/dags/startup_report_etl/dagRuns
```

## Environment Variables

The AirflowClient can be configured via environment variables:

- `AIRFLOW_USERNAME`: Username for authentication (default: 'admin')
- `AIRFLOW_PASSWORD`: Password for authentication (default: set in code)

## Troubleshooting

If you get authentication errors:

1. Verify Airflow is running: `curl http://localhost:8080/api/v2/monitor/health`
2. Check that the username and password match the configured users in `simple_auth_manager_users` in `~/airflow/airflow.cfg`
3. Ensure the Simple Auth Manager is configured:
   ```ini
   auth_manager = airflow.api_fastapi.auth.managers.simple.simple_auth_manager.SimpleAuthManager
   simple_auth_manager_users = admin:your-password
   ```

## How It Works

1. When `trigger_dag()` is called, the client checks if it has a JWT token
2. If not, it fetches one from `/auth/token` using username/password
3. The token is used for the API request with `Authorization: Bearer <token>`
4. If the request returns 401 (unauthorized), the client:
   - Clears the old token
   - Fetches a fresh token
   - Retries the request automatically
