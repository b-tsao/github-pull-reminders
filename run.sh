#!/bin/bash

export SLACK_WEBHOOK=""
export GITHUB_URL="https://github.<domain>.com"
export GITHUB_API_TOKEN=""
export ORGANIZATION=""
export REPOSITORIES=""

echo "[$(date '+%d/%m/%Y %H:%M:%S')] Running pull reminder..."
python3 slack_pull_reminder.py
echo "[$(date '+%d/%m/%Y %H:%M:%S')] Completed pull reminder"
