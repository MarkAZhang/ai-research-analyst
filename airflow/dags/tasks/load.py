"""Load task: Update the report with final text and set status to completed."""

import os
import sqlite3
from airflow.sdk import task


# Database path - use absolute path to avoid symlink issues
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
def load(transformed_data: dict) -> None:
    """Load: Update the report with final text and set status to completed.

    Args:
        transformed_data: Dictionary from transform step containing final_text
    """
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
