# Screenshot Cleanup Utility

Automatically deletes old screenshot and HTML files from the `screenshots/` directory.

## Features

- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ Configurable retention period (default: 7 days)
- ✅ Dry-run mode to preview deletions
- ✅ Detailed logging with file age and size
- ✅ Preserves `.gitkeep` file
- ✅ Supports both `.png` and `.html` files

## Usage

### Basic Usage

```bash
# Delete files older than 7 days (default)
python cleanup_screenshots.py
```

### Custom Retention Period

```bash
# Keep files for 30 days
python cleanup_screenshots.py --days 30

# Keep files for 1 day (aggressive cleanup)
python cleanup_screenshots.py --days 1
```

### Dry Run Mode

Preview what would be deleted without actually deleting:

```bash
# See what would be deleted with default 7-day retention
python cleanup_screenshots.py --dry-run

# See what would be deleted with custom retention
python cleanup_screenshots.py --days 14 --dry-run
```

## Automated Cleanup

### Linux/Mac - Cron Job

Add to your crontab (`crontab -e`):

```bash
# Run daily at 2:00 AM
0 2 * * * cd /path/to/web-transaction-monitor && /usr/bin/python3 cleanup_screenshots.py --days 7
```

### Windows - Task Scheduler

```powershell
# Create scheduled task (run as Administrator)
schtasks /create /tn "Cleanup Screenshots" /tr "python C:\path\to\web-transaction-monitor\cleanup_screenshots.py --days 7" /sc daily /st 02:00 /ru SYSTEM
```

Or use the Task Scheduler GUI:
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Cleanup Screenshots"
4. Trigger: Daily at 2:00 AM
5. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\web-transaction-monitor\cleanup_screenshots.py --days 7`
   - Start in: `C:\path\to\web-transaction-monitor`

### Docker Container

**Already Integrated!** The Docker Compose stack includes an automated cleanup service that runs daily.

The `screenshot-cleanup` service:
- Runs every 24 hours automatically
- Deletes files older than 7 days
- Starts with the stack (`docker-compose up`)
- Logs visible via `docker-compose logs -f screenshot-cleanup`

#### Customize Retention Period

Edit `docker-compose.yml` and change `--days 7` to your preferred retention:

```yaml
screenshot-cleanup:
  # ... other config ...
  command: >
    sh -c "while true; do
      python cleanup_screenshots.py --days 30;  # Change this number
      sleep 86400;
    done"
```

#### Manual Cleanup in Docker

Run cleanup manually from inside the container:

```bash
# One-time cleanup with default 7-day retention
docker-compose exec monitor-app python cleanup_screenshots.py

# Custom retention period
docker-compose exec monitor-app python cleanup_screenshots.py --days 14

# Dry run to see what would be deleted
docker-compose exec monitor-app python cleanup_screenshots.py --dry-run
```

## Output Example

```
2026-01-12 10:00:00,123 - INFO - Cleaning up files older than 7 days (before 2026-01-05 10:00:00)
2026-01-12 10:00:00,234 - INFO - Deleting: hidrive-next_picture_test_02_Cookie___Login_step_failure_20260104_153045.png (age: 8.2 days, size: 234.5 KB)
2026-01-12 10:00:00,345 - INFO - Deleting: hidrive-next_picture_test_02_Cookie___Login_step_failure_20260104_153045.html (age: 8.2 days, size: 145.3 KB)
2026-01-12 10:00:00,456 - INFO - Freed 0.37 MB by deleting 2 file(s)
```

## Help

```bash
python cleanup_screenshots.py --help
```

## Notes

- The script never deletes the `.gitkeep` file
- Only files with `.png` and `.html` extensions are processed
- File age is determined by modification time (mtime)
- The script is safe to run multiple times - it's idempotent
