"""Transform task: Hydrate prompt with name, send to OpenAI API, and return LLM response."""

import os
import sqlite3
from airflow.sdk import task
from openai import OpenAI


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
def transform(extracted_data: dict) -> dict:
    """Transform: Hydrate prompt with name, send to OpenAI API, and return LLM response.

    Args:
        extracted_data: Dictionary from extract step containing name and prompt_text

    Returns:
        Dictionary with report_id and final_text (OpenAI response)
    """
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
