"""
Airflow DAG for processing startup reports with ETL pipeline.

This DAG performs the following steps:
1. Extract: Fetch the StartupReport's name and prompt text from SQLite database
2. Transform: Hydrate prompt with name, send to OpenAI API, and receive LLM response
3. Load: Update the report with the final text and set status to completed/failed
"""

import os
from datetime import datetime
from pathlib import Path

from airflow.sdk import dag, task, Param
from dotenv import load_dotenv

# Database path - use absolute path to avoid symlink issues
# When DAG is accessed via symlink, we need to resolve to the real path
dag_file_path = os.path.realpath(__file__)
backend_dir = os.path.dirname(os.path.dirname(dag_file_path))
DB_PATH = os.path.join(backend_dir, "dev.sqlite3")

# Load environment variables from .env file
env_path = Path(backend_dir) / ".env"
load_dotenv(dotenv_path=env_path)


def _set_report_failed(context):
    """Helper function to set report status to failed when DAG fails."""
    import sqlite3

    report_id = context["params"]["report_id"]

    conn = sqlite3.connect(DB_PATH)
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


@dag(
    dag_id="startup_report_etl",
    schedule=None,  # Only triggered manually/programmatically
    start_date=datetime(2025, 1, 1),
    catchup=False,
    params={
        "report_id": Param(
            default=None,
            type=["null", "integer"],
            description="ID of the StartupReportDbModel to process",
        )
    },
    tags=["startup_report", "etl"],
)
def startup_report_etl_dag():
    """ETL pipeline for processing startup reports."""

    @task(on_failure_callback=_set_report_failed)
    def extract(report_id: int) -> dict:
        """Extract: Fetch the StartupReport's name and prompt text from database.

        Args:
            report_id: ID of the report to process

        Returns:
            Dictionary containing report_id, name, and prompt_text
        """
        import sqlite3

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            # Fetch report with its associated prompt
            cursor.execute(
                """
                SELECT r.name, p.prompt
                FROM core_startupreport r
                LEFT JOIN core_startupreportprompt p ON r.prompt_id = p.id
                WHERE r.id = ?
            """,
                (report_id,),
            )

            result = cursor.fetchone()

            if not result:
                raise ValueError(f"Report with ID {report_id} does not exist")

            name, prompt_text = result

            if not prompt_text:
                raise ValueError(f"Report {report_id} has no associated prompt")

            return {
                "report_id": report_id,
                "name": name,
                "prompt_text": prompt_text,
            }
        finally:
            conn.close()

    @task(on_failure_callback=_set_report_failed)
    def transform(extracted_data: dict) -> dict:
        """Transform: Hydrate prompt with name, send to OpenAI API, and return LLM response.

        Args:
            extracted_data: Dictionary from extract step containing name and prompt_text

        Returns:
            Dictionary with report_id and final_text (OpenAI response)
        """
        import os
        from openai import OpenAI

        name = extracted_data["name"]
        prompt_text = extracted_data["prompt_text"]

        # Replace {{name}} with the actual name
        hydrated_prompt = prompt_text.replace("{{name}}", name)

        # Initialize OpenAI client with API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        client = OpenAI(api_key=api_key)

        # Call OpenAI API with the hydrated prompt
        response = client.chat.completions.create(
            model="gpt-4o-mini-search-preview",
            web_search_options={
                # Optional: configure search context size ('low', 'medium', 'high')
                "search_context_size": "medium",
            },
            messages=[{"role": "user", "content": hydrated_prompt}],
        )

        # Extract the LLM response text
        final_text = response.choices[0].message.content

        return {
            "report_id": extracted_data["report_id"],
            "final_text": final_text,
        }

    @task(on_failure_callback=_set_report_failed)
    def load(transformed_data: dict) -> None:
        """Load: Update the report with final text and set status to completed.

        Args:
            transformed_data: Dictionary from transform step containing final_text
        """
        import sqlite3

        report_id = transformed_data["report_id"]
        final_text = transformed_data["final_text"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE core_startupreport
                SET report_text = ?, generation_status = 'completed'
                WHERE id = ?
            """,
                (final_text, report_id),
            )

            conn.commit()
        finally:
            conn.close()

    # Get report_id from params (templated value)
    report_id = "{{ params.report_id }}"  # type: ignore[reportArgumentType]

    # Define the ETL pipeline flow
    extracted_data = extract(report_id)  # type: ignore[reportArgumentType]
    transformed_data = transform(extracted_data)  # type: ignore[reportArgumentType]
    load(transformed_data)  # type: ignore[reportArgumentType]


# Instantiate the DAG
startup_report_etl = startup_report_etl_dag()
