# Airflow Setup for REST API Access

This document explains how to configure Apache Airflow 3.x to work with the Django application via the REST API.

## Configuration

The AirflowClient in `backend/core/airflow_client.py` uses the Airflow REST API (v2) to trigger DAGs from Django.

### Enable Basic Authentication for API

For Airflow 3.x to accept REST API requests with HTTP Basic Authentication, you need to configure the `api_auth` backend in `~/airflow/airflow.cfg`:

```ini
[api_auth]
backend = airflow.api.auth.backend.basic_auth
```

### Restart Airflow

After making configuration changes, restart Airflow:

```bash
# If running in standalone mode
# Stop the current process (Ctrl+C) and restart:
airflow standalone

# Or if running individual components:
# Restart the webserver
pkill -f "airflow webserver"
airflow webserver -D
```

## Testing the REST API

You can test the REST API configuration using curl:

```bash
# List DAGs
curl -X GET \
  -u admin:admin \
  http://localhost:8080/api/v2/dags

# Trigger a DAG
curl -X POST \
  -u admin:admin \
  -H "Content-Type: application/json" \
  -d '{"conf": {"report_id": 1}}' \
  http://localhost:8080/api/v2/dags/startup_report_etl/dagRuns
```

## Environment Variables

The AirflowClient can be configured via environment variables:

- `AIRFLOW_USERNAME`: Username for basic auth (default: 'admin')
- `AIRFLOW_PASSWORD`: Password for basic auth (default: 'admin')

## Troubleshooting

If you get "Not authenticated" errors:

1. Verify that `[api_auth] backend = airflow.api.auth.backend.basic_auth` is set in `~/airflow/airflow.cfg`
2. Restart the Airflow webserver
3. Check that the username and password match the configured users in `simple_auth_manager_users`
