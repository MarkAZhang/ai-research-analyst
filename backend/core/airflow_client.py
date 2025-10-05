"""Utility module for triggering Airflow DAGs from Django."""
import json
import os
import subprocess
from typing import Any


class AirflowClient:
    """Client for interacting with Airflow via CLI."""

    def __init__(self, airflow_home: str = "~/airflow"):
        """Initialize the Airflow client.

        Args:
            airflow_home: Path to Airflow home directory
        """
        self.airflow_home = os.path.expanduser(airflow_home)

    def trigger_dag(self, dag_id: str, conf: dict[str, Any] | None = None) -> bool:
        """Trigger an Airflow DAG run using the Airflow CLI.

        Args:
            dag_id: ID of the DAG to trigger
            conf: Configuration parameters to pass to the DAG

        Returns:
            True if successful, False otherwise
        """
        try:
            # Build the command
            cmd = [
                "airflow",
                "dags",
                "trigger",
                dag_id,
            ]

            # Add conf parameter if provided
            if conf:
                cmd.extend(["--conf", json.dumps(conf)])

            # Set environment with AIRFLOW_HOME
            env = os.environ.copy()
            env["AIRFLOW_HOME"] = self.airflow_home

            # Execute the command
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                print(f"Successfully triggered DAG {dag_id}")
                return True
            else:
                print(f"Error triggering DAG {dag_id}: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error triggering DAG {dag_id}: {e}")
            return False


# Global client instance
airflow_client = AirflowClient()
