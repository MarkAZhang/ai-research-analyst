"""Extract task: Fetch the StartupReport's name and prompt text from database."""

import os
import sqlite3
from airflow.sdk import task


# Database path - use absolute path to avoid symlink issues
# When DAG is accessed via symlink, we need to resolve to the real path
dag_file_path = os.path.realpath(__file__)
dags_dir = os.path.dirname(os.path.dirname(dag_file_path))
backend_dir = os.path.dirname(dags_dir)
DB_PATH = os.path.join(backend_dir, "dev.sqlite3")


def _set_report_failed(context):
    """Helper function to set report status to failed when task fails."""
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


@task(on_failure_callback=_set_report_failed)
def extract(report_id: int) -> dict:
    """Extract: Fetch the StartupReport's name and prompt text from database.

    Args:
        report_id: ID of the report to process

    Returns:
        Dictionary containing report_id, name, and prompt_text
    """
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
