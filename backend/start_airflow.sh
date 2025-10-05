#!/bin/bash

# Set Airflow home directory
export AIRFLOW_HOME=~/airflow

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set the DAGs folder to the project's dags directory
export AIRFLOW__CORE__DAGS_FOLDER="$SCRIPT_DIR/dags"

# Run Airflow in standalone mode
# This will start the webserver, scheduler, and create an admin user automatically
airflow standalone
