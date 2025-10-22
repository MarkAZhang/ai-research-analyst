"""Extract task: Fetch the StartupReport's name and prompt text from database."""

import sqlite3
from airflow.sdk import task

from common import DB_PATH, set_report_failed


@task(on_failure_callback=set_report_failed)
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
