#!/bin/bash
# Cleanup script for orphaned Playwright/Chromium processes
# Runs periodically inside the monitor-app container

echo "[$(date)] Checking for orphaned browser processes..."

# Find and kill orphaned chromium processes older than 10 minutes
# Exclude: grep, python (main process), and the current bash script
for pid in $(ps aux | grep -E 'chromium|chrome|node.*playwright' | grep -v grep | grep -v 'python' | awk '{print $2}'); do
    # Check process age (in seconds)
    age=$(ps -o etimes= -p $pid 2>/dev/null | tr -d ' ')
    if [ -n "$age" ] && [ "$age" -gt 600 ]; then
        echo "[$(date)] Killing orphaned process $pid (age: ${age}s)"
        kill -9 $pid 2>/dev/null || true
    fi
done

echo "[$(date)] Cleanup completed"
