#!/usr/bin/env python3
"""
Screenshot Cleanup Script
Deletes screenshots and HTML files older than specified days from the screenshots directory.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
DEFAULT_RETENTION_DAYS = 7
FILE_EXTENSIONS = [".png", ".html"]


def cleanup_old_files(retention_days: int = DEFAULT_RETENTION_DAYS, dry_run: bool = False) -> tuple[int, int]:
    """
    Delete screenshot and HTML files older than retention_days.
    
    Args:
        retention_days: Number of days to keep files
        dry_run: If True, only show what would be deleted without actually deleting
        
    Returns:
        Tuple of (files_deleted, total_size_freed_bytes)
    """
    if not SCREENSHOTS_DIR.exists():
        logger.warning(f"Screenshots directory does not exist: {SCREENSHOTS_DIR}")
        return 0, 0
    
    cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
    cutoff_date = datetime.fromtimestamp(cutoff_time)
    
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Cleaning up files older than {retention_days} days (before {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')})")
    
    files_deleted = 0
    total_size_freed = 0
    
    for file_path in SCREENSHOTS_DIR.iterdir():
        # Skip directories and .gitkeep
        if file_path.is_dir() or file_path.name == ".gitkeep":
            continue
        
        # Only process screenshot and HTML files
        if file_path.suffix.lower() not in FILE_EXTENSIONS:
            continue
        
        # Check file age
        file_mtime = file_path.stat().st_mtime
        
        if file_mtime < cutoff_time:
            file_size = file_path.stat().st_size
            file_age_days = (time.time() - file_mtime) / (24 * 60 * 60)
            
            logger.info(f"{'[DRY RUN] Would delete' if dry_run else 'Deleting'}: {file_path.name} (age: {file_age_days:.1f} days, size: {file_size / 1024:.1f} KB)")
            
            if not dry_run:
                try:
                    file_path.unlink()
                    files_deleted += 1
                    total_size_freed += file_size
                except Exception as e:
                    logger.error(f"Failed to delete {file_path.name}: {e}")
            else:
                files_deleted += 1
                total_size_freed += file_size
    
    size_mb = total_size_freed / (1024 * 1024)
    logger.info(f"{'[DRY RUN] Would free' if dry_run else 'Freed'} {size_mb:.2f} MB by deleting {files_deleted} file(s)")
    
    return files_deleted, total_size_freed


def main():
    """Main entry point for the cleanup script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up old screenshots and HTML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Delete files older than 7 days (default)
  python cleanup_screenshots.py
  
  # Delete files older than 30 days
  python cleanup_screenshots.py --days 30
  
  # Dry run - show what would be deleted without actually deleting
  python cleanup_screenshots.py --dry-run
  
  # Delete files older than 14 days with dry run
  python cleanup_screenshots.py --days 14 --dry-run
        """
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help=f'Number of days to retain files (default: {DEFAULT_RETENTION_DAYS})'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting files'
    )
    
    args = parser.parse_args()
    
    if args.days < 1:
        logger.error("Retention days must be at least 1")
        sys.exit(1)
    
    try:
        files_deleted, size_freed = cleanup_old_files(
            retention_days=args.days,
            dry_run=args.dry_run
        )
        
        if files_deleted == 0:
            logger.info("No files to delete")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
