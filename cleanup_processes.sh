#!/bin/bash
# Cleanup script for orphaned Playwright/Chromium processes
# Runs periodically inside the monitor-app container

echo "[$(date)] Checking for orphaned browser processes..."

# Find and kill orphaned chromium processes older than 10 minutes
# (Legitimate tests should finish within the timeout)
for pid in $(ps aux | grep -E 'chromium|playwright' | grep -v grep | awk '{print $2}'); do
    # Check process age (in seconds)
    age=$(ps -o etimes= -p $pid 2>/dev/null | tr -d ' ')
    if [ -n "$age" ] && [ "$age" -gt 600 ]; then
        echo "[$(date)] Killing orphaned process $pid (age: ${age}s)"
        kill -9 $pid 2>/dev/null || true
    fi
done

echo "[$(date)] Cleanup completed"
