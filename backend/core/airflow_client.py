"""Utility module for triggering Airflow DAGs from Django."""

import os
from datetime import datetime, timezone
from typing import Any

import requests


class AirflowClient:
    """Client for interacting with Airflow via REST API.

    For Airflow 3.x, uses JWT token authentication with the Simple Auth Manager.
    Tokens are fetched using username/password and automatically refreshed on 401 errors.
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
            username: Username for authentication (optional, defaults to 'admin')
            password: Password for authentication (optional, defaults to env var or 'DHWnYWpeRt2msVRP')
        """
        self.base_url = base_url.rstrip("/")
        self.username = username or os.getenv("AIRFLOW_USERNAME", "admin")
        self.password = password or os.getenv("AIRFLOW_PASSWORD", "DHWnYWpeRt2msVRP")
        self.session = requests.Session()
        self._jwt_token: str | None = None

    def _fetch_jwt_token(self) -> bool:
        """Fetch a JWT token from Airflow using username/password.

        Returns:
            True if token was successfully fetched, False otherwise
        """
        try:
            token_url = f"{self.base_url}/auth/token"
            payload = {
                "username": self.username,
                "password": self.password,
            }

            response = self.session.post(
                token_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code in (200, 201):
                data = response.json()
                self._jwt_token = data.get("access_token")
                if self._jwt_token:
                    # Set the Authorization header for future requests
                    self.session.headers.update(
                        {"Authorization": f"Bearer {self._jwt_token}"}
                    )
                    return True
                else:
                    print("No access_token in response")
                    return False
            else:
                print(
                    f"Failed to fetch JWT token: "
                    f"Status {response.status_code}, {response.text}"
                )
                return False

        except Exception as e:
            print(f"Error fetching JWT token: {e}")
            return False

    def _ensure_authenticated(self) -> bool:
        """Ensure the client has a valid JWT token.

        Returns:
            True if authenticated (has token), False otherwise
        """
        if self._jwt_token:
            return True

        return self._fetch_jwt_token()

    def trigger_dag(self, dag_id: str, conf: dict[str, Any] | None = None) -> bool:
        """Trigger an Airflow DAG run using the REST API.

        Automatically fetches a JWT token if not already authenticated.
        If a 401 error is encountered, refreshes the token and retries once.

        Args:
            dag_id: ID of the DAG to trigger
            conf: Configuration parameters to pass to the DAG

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure we have a valid JWT token
            if not self._ensure_authenticated():
                print("Failed to authenticate with Airflow")
                return False

            # Construct the API endpoint (v2 for Airflow 3.x)
            url = f"{self.base_url}/api/v2/dags/{dag_id}/dagRuns"

            # Build the request payload
            # Include logical_date (required in Airflow 3.x)
            payload: dict[str, Any] = {
                "logical_date": datetime.now(timezone.utc).isoformat(),
            }
            if conf:
                payload["conf"] = conf

            # Make the POST request to trigger the DAG
            response = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            # Handle 401 errors by refreshing the token and retrying
            if response.status_code == 401:
                print("Received 401, refreshing JWT token and retrying...")
                # Clear the old token
                self._jwt_token = None
                self.session.headers.pop("Authorization", None)

                # Fetch a new token
                if not self._fetch_jwt_token():
                    print("Failed to refresh JWT token")
                    return False

                # Retry the request with the new token
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
