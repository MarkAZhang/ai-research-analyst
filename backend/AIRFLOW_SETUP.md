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
- DAGs folder: `~/airflow/dags`

### Creating DAGs

Place your DAG files in the `~/airflow/dags` directory. Airflow will automatically detect and load them.

### Stopping Airflow

Press `Ctrl+C` in the terminal where Airflow standalone is running.
