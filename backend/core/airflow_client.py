"""Utility module for triggering Airflow DAGs from Django."""
import os
from typing import Any

import requests
from requests.auth import HTTPBasicAuth


class AirflowClient:
    """Client for interacting with Airflow via REST API.

    For Airflow 3.x, uses HTTP Basic Authentication for the REST API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        username: str | None = None,
        password: str | None = None,
    ):
        """Initialize the Airflow client.

        Args:
            base_url: Base URL of the Airflow webserver (default: http://localhost:8080)
            username: Username for basic auth (optional, defaults to 'admin')
            password: Password for basic auth (optional, defaults to 'admin')
        """
        self.base_url = base_url.rstrip("/")
        self.username = username or os.getenv("AIRFLOW_USERNAME", "admin")
        self.password = password or os.getenv("AIRFLOW_PASSWORD", "admin")
        self.session = requests.Session()
        # Use HTTP Basic Authentication
        self.session.auth = HTTPBasicAuth(self.username, self.password)

    def trigger_dag(self, dag_id: str, conf: dict[str, Any] | None = None) -> bool:
        """Trigger an Airflow DAG run using the REST API.

        Args:
            dag_id: ID of the DAG to trigger
            conf: Configuration parameters to pass to the DAG

        Returns:
            True if successful, False otherwise
        """
        try:
            # Construct the API endpoint (v2 for Airflow 3.x)
            url = f"{self.base_url}/api/v2/dags/{dag_id}/dagRuns"

            # Build the request payload
            payload: dict[str, Any] = {}
            if conf:
                payload["conf"] = conf

            # Make the POST request to trigger the DAG
            response = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code in (200, 201):
                print(f"Successfully triggered DAG {dag_id}")
                return True
            else:
                print(
                    f"Error triggering DAG {dag_id}: "
                    f"Status {response.status_code}, {response.text}"
                )
                return False

        except Exception as e:
            print(f"Error triggering DAG {dag_id}: {e}")
            return False


# Global client instance
airflow_client = AirflowClient()
