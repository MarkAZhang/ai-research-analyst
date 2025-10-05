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

To start Airflow in standalone mode (includes webserver, scheduler, and creates an admin user):

```bash
./start_airflow.sh
```

Or manually:
```bash
export AIRFLOW_HOME=~/airflow
airflow standalone
```

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
2. **Django Access**: DAGs can import and use Django models by:
   - Adding the backend directory to Python path
   - Configuring Django settings
   - Importing models after `django.setup()`

3. **Triggering DAGs from Django**:
   - Use the `AirflowClient` in `core/airflow_client.py`
   - Example: `airflow_client.trigger_dag('dag_id', conf={'param': 'value'})`

### Startup Report ETL Pipeline

The `startup_report_etl` DAG performs the following:

1. **Extract**: Fetches the StartupReport's name and prompt text from the database
2. **Transform**: Replaces `{{name}}` placeholders in the prompt with the actual startup name
3. **Load**: Updates the report with the final text and sets status to 'completed' (or 'failed' on error)

This DAG is automatically triggered when new startup reports are created via the API.

### Creating DAGs

Place your DAG files in the `backend/dags/` directory. Airflow will automatically detect and load them.

To access Django models in your DAG:
```python
import os
import sys
import django

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

# Now import Django models
from core.startup_report.db.startup_report_db_model import StartupReportDbModel
```

### Stopping Airflow

Press `Ctrl+C` in the terminal where Airflow standalone is running.
