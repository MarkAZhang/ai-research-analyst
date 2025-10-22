"""Load task: Update the report with final text and set status to completed."""

import sqlite3
from airflow.sdk import task

from common import DB_PATH, set_report_failed


@task(on_failure_callback=set_report_failed)
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
