# Airflow Setup Guide

This project uses Apache Airflow 3.1.0 for workflow orchestration.

## Local Development Setup

### Prerequisites
- Python 3.12+
- pip-tools (for managing requirements)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The Airflow database has already been initialized. If you need to reset it:
```bash
export AIRFLOW_HOME=~/airflow
airflow db migrate
```

### Running Airflow

To start Airflow in standalone mode:

```bash
./start_airflow.sh
```

The script will:
- Set AIRFLOW_HOME to ~/airflow
- Create a symlink from ~/airflow/dags to backend/dags
- Start Airflow in standalone mode (webserver, scheduler, and creates admin user)

### Accessing the Airflow UI

Once Airflow is running, you can access the web UI at:
- URL: http://localhost:8080
- The standalone command will display the admin credentials in the terminal output

### Configuration

- Airflow home directory: `~/airflow`
- Configuration file: `~/airflow/airflow.cfg`
- DAGs folder: `backend/dags` (configured in start_airflow.sh)

## Django-Airflow Integration

### How It Works

1. **DAG Location**: DAGs are stored in `backend/dags/`
2. **Database Access**: DAGs access the Django database directly using SQLite connections
   - Database path: `backend/dev.sqlite3`
   - Uses raw SQL queries via `sqlite3` module
   - No Django ORM dependencies in DAGs

3. **Triggering DAGs from Django**:
   - Use the `AirflowClient` in `core/airflow_client.py`
   - The client uses the Airflow CLI to trigger DAGs (not the REST API)
   - Example: `airflow_client.trigger_dag('dag_id', conf={'param': 'value'})`
   - Returns `True` if successful, `False` otherwise

### Startup Report ETL Pipeline

The `startup_report_etl` DAG performs the following:

1. **Extract**: Fetches the StartupReport's name and prompt text from the database
2. **Transform**: Replaces `{{name}}` placeholders in the prompt with the actual startup name
3. **Load**: Updates the report with the final text and sets status to 'completed' (or 'failed' on error)

This DAG is automatically triggered when new startup reports are created via the API.

### Creating DAGs

Place your DAG files in the `backend/dags/` directory. Airflow will automatically detect and load them.

To access the Django database in your DAG:
```python
import os
import sqlite3

# Get database path - use realpath to resolve symlinks
dag_file_path = os.path.realpath(__file__)
backend_dir = os.path.dirname(os.path.dirname(dag_file_path))
DB_PATH = os.path.join(backend_dir, 'dev.sqlite3')

# Use SQLite connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT * FROM core_startupreport WHERE id = ?", (report_id,))
result = cursor.fetchone()

conn.close()
```

**Note**: DAGs use direct SQLite connections instead of Django ORM to avoid import dependencies and simplify the setup.

### Stopping Airflow

Press `Ctrl+C` in the terminal where Airflow standalone is running.
