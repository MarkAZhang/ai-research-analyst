#!/bin/bash

# Set Airflow home directory
export AIRFLOW_HOME=~/airflow

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Add backend directory to PYTHONPATH so DAGs can import Django modules
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Create symlink for DAGs folder if it doesn't exist
if [ ! -L "$AIRFLOW_HOME/dags" ]; then
    ln -sfn "$SCRIPT_DIR/dags" "$AIRFLOW_HOME/dags"
fi

# Run Airflow in standalone mode
# This will start the webserver, scheduler, and create an admin user automatically
airflow standalone
