"""Common utilities and configuration for Airflow DAGs."""

import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv


def get_airflow_dir() -> str:
    """Get the airflow directory path.

    Returns:
        Absolute path to the airflow directory
    """
    # Get the directory where this common.py file is located (dags/)
    dags_dir = os.path.dirname(os.path.realpath(__file__))
    # Go up one level to get airflow/
    airflow_dir = os.path.dirname(dags_dir)
    return airflow_dir


def get_backend_dir() -> str:
    """Get the backend directory path.

    Returns:
        Absolute path to the backend directory
    """
    airflow_dir = get_airflow_dir()
    # Go up one level from airflow/ to project root, then into backend/
    project_root = os.path.dirname(airflow_dir)
    backend_dir = os.path.join(project_root, "backend")
    return backend_dir


def get_db_path() -> str:
    """Get the database path.

    Returns:
        Absolute path to the SQLite database
    """
    backend_dir = get_backend_dir()
    return os.path.join(backend_dir, "dev.sqlite3")


def load_environment():
    """Load environment variables from .env file in airflow directory."""
    airflow_dir = get_airflow_dir()
    env_path = Path(airflow_dir) / ".env"
    load_dotenv(dotenv_path=env_path)


def set_report_failed(context):
    """Helper function to set report status to failed when a task fails.

    This is designed to be used as an on_failure_callback for Airflow tasks.

    Args:
        context: Airflow task context containing params
    """
    report_id = context["params"]["report_id"]
    db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE core_startupreport
            SET generation_status = 'failed'
            WHERE id = ?
        """,
            (report_id,),
        )

        conn.commit()
    except Exception as e:
        print(f"Error setting failure status for report {report_id}: {e}")
    finally:
        conn.close()


# Module-level constants
DB_PATH = get_db_path()
AIRFLOW_DIR = get_airflow_dir()
BACKEND_DIR = get_backend_dir()
