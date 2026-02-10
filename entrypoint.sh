#!/bin/bash
# Entrypoint script that starts both the cleanup cron and the main application

# Start cleanup cron in background (every 10 minutes)
(
  while true; do
    /app/cleanup_processes.sh
    sleep 600  # 10 minutes
  done
) &

# Start main application
exec python main.py
