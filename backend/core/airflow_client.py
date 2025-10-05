"""Utility module for triggering Airflow DAGs from Django."""
import requests
from typing import Any


class AirflowClient:
    """Client for interacting with Airflow API."""

    def __init__(self, base_url: str = "http://localhost:8080", username: str = "admin", password: str = "admin"):
        """Initialize the Airflow client.

        Args:
            base_url: Base URL of the Airflow webserver
            username: Airflow username for authentication
            password: Airflow password for authentication
        """
        self.base_url = base_url
        self.auth = (username, password)

    def trigger_dag(self, dag_id: str, conf: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Trigger an Airflow DAG run.

        Args:
            dag_id: ID of the DAG to trigger
            conf: Configuration parameters to pass to the DAG

        Returns:
            Response from the Airflow API, or None if failed
        """
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns"

        payload = {
            "conf": conf or {},
        }

        try:
            response = requests.post(
                url,
                json=payload,
                auth=self.auth,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error triggering DAG {dag_id}: {e}")
            return None


# Global client instance
airflow_client = AirflowClient()
