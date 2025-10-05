#!/bin/bash

# Set Airflow home directory
export AIRFLOW_HOME=~/airflow

# Run Airflow in standalone mode
# This will start the webserver, scheduler, and create an admin user automatically
airflow standalone
