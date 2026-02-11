#!/bin/bash
# Entrypoint script that starts both the cleanup cron and the main application

# Ensure scripts have execute permissions (in case of volume mounts)
chmod +x /app/cleanup_processes.sh 2>/dev/null || true

# Start cleanup cron in background (every 10 minutes)
(
  while true; do
    bash /app/cleanup_processes.sh
    sleep 600  # 10 minutes
  done
) &

# Start main application with auto-restart on crash
while true; do
  echo "[$(date)] Starting main.py..."
  python main.py
  EXIT_CODE=$?
  echo "[$(date)] main.py exited with code $EXIT_CODE. Restarting in 10 seconds..."
  sleep 10
done
