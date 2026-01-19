import os
import time
import glob
import logging
from typing import Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from prometheus_client import start_http_server
from runners.python_runner import PythonRunner

# Configuration
METRICS_PORT = int(os.getenv('PROMETHEUS_PORT', 8000))
CHECK_INTERVAL_SECONDS = int(os.getenv('SCHEDULE_INTERVAL', 300)) # Default 5 mins

# Logging - respect DEBUG environment variable
debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

if debug_mode:
    # DEBUG mode: Show everything
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    # Production mode: Only show transaction START/SUCCESS/FAILED (from monitor_base)
    logging.basicConfig(
        level=logging.ERROR,  # Suppress most logs
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # But allow monitor_base to log at INFO level for transactions
    logging.getLogger('monitor_base').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

def load_and_schedule_usecases(scheduler: BackgroundScheduler) -> None:
    transactions_dir = os.path.join(os.path.dirname(__file__), 'transactions')
    logger.info(f"Scanning for transactions in {transactions_dir}")
    
    python_runner = PythonRunner()
    
    # Discover Python files (Recursively)
    py_files = glob.glob(os.path.join(transactions_dir, '**', '*.py'), recursive=True)
    JOB_TIMEOUT_SECONDS = int(os.getenv('JOB_TIMEOUT_SECONDS', 240))  # Default: 4 min per job
    for i, py_file in enumerate(py_files):
        if os.path.basename(py_file).startswith('__'): 
            continue
        # Create a cleaner job ID from path relative to transactions dir
        rel_path = os.path.relpath(py_file, transactions_dir)
        # Flatten path to name: subdir/test.py -> subdir_test
        name = os.path.splitext(rel_path)[0].replace(os.sep, '_')
        job_id = f"python_{name}"
        # Stagger start times by 1 second to ensure sequential execution doesn't skip
        start_time = datetime.now() + timedelta(seconds=i)
        def run_with_timeout(py_file=py_file, name=name):
            import threading
            result = {'done': False}
            def target():
                try:
                    python_runner.run(py_file, name)
                except Exception as e:
                    logger.error(f"Job {name} crashed: {e}")
                finally:
                    result['done'] = True
            t = threading.Thread(target=target)
            t.start()
            t.join(JOB_TIMEOUT_SECONDS)
            if t.is_alive():
                logger.error(f"Job {name} exceeded timeout ({JOB_TIMEOUT_SECONDS}s) and will be skipped.")
                # Optionally: set metrics to failure
                from monitor_base import TRANS_SUCCESS, TRANS_LAST_RUN
                TRANS_SUCCESS.labels(usecase=name).set(0)
                TRANS_LAST_RUN.labels(usecase=name).set_to_current_time()
                # Try to clean up resources if possible (not always possible)
                # Note: Python cannot forcibly kill threads, so this is a best-effort
        scheduler.add_job(
            run_with_timeout,
            'interval',
            seconds=CHECK_INTERVAL_SECONDS,
            next_run_time=start_time,
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled Python Monitor: {name} (starting at {start_time})")

def main() -> None:
    logger.info(f"Starting Metrics Server on port {METRICS_PORT}...")
    start_http_server(METRICS_PORT)
    
    # Configure scheduler for SEQUENTIAL execution
    executors = {
        'default': ThreadPoolExecutor(1)  # Only 1 worker means jobs run one after another
    }
    job_defaults = {
        'coalesce': True,  # Combine multiple missed runs into one
        'max_instances': 1,  # Never run the same job twice at the same time
        'misfire_grace_time': None  # Always run missed jobs, no matter how late
    }
    
    scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
    load_and_schedule_usecases(scheduler)
    
    logger.info("Starting Scheduler (Sequential Mode)...")
    scheduler.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    main()
