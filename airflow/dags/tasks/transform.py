"""Transform task: Hydrate prompt with name, send to OpenAI API, and return LLM response."""

import os
from airflow.sdk import task
from openai import OpenAI

from common import set_report_failed


@task(on_failure_callback=set_report_failed)
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
        model="gpt-5-search-api",
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
