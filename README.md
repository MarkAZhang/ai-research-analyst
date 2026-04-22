# AI Research Analyst

Request research reports for multiple startups.

Small personal project to explore prompt engineering and LLMs for research.

## Screenshots

Request reports for one or more startups.

<img src="docs/screenshots/1_request_reports.png" alt="Request Reports Screenshot" width="300">

Edit the prompt if desired. Prompts are versioned and linked to generated reports.

<img src="docs/screenshots/2_edit_prompt.png" alt="Edit Prompt Screenshot" width="300">

Report generation in the background with Airflow.

<img src="docs/screenshots/3_processing.png" alt="Processing Screenshot" width="300">

View generated report when finished.

<img src="docs/screenshots/4_report_view.png" alt="Report View Screenshot" width="300">

## Local Development Setup

Start the frontend

```
cd frontend
npm run dev
```

Start the backend

```
cd backend
python manage.py runserver 8081
```

Start Airflow

```
cd airflow
./start_airflow.sh
```

Access the website at localhost:3000.
