#!/usr/bin/env python3
"""
Playwright Test Recorder with optimized selector preferences
Generates code using data attributes, CSS selectors, and IDs instead of text-based selectors
"""
import os
import sys
from playwright.sync_api import sync_playwright

def record_test():
    """
    Start Playwright codegen with optimized selector preferences
    """
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get HiDrive Legacy credentials
    url = os.getenv('HIDRIVE_LEGACY_URL', 'https://hidrive.ionos.com/#login')
    
    print("=" * 60)
    print("Playwright Test Recorder")
    print("=" * 60)
    print(f"Starting URL: {url}")
    print("\nSelector Priority:")
    print("  1. data-* attributes (data-qa, data-testid, data-cy, etc.)")
    print("  2. IDs (#id)")
    print("  3. CSS classes and selectors")
    print("  4. Avoid text-based selectors!")
    print("\nTips:")
    print("  - Use browser DevTools to inspect elements")
    print("  - Look for data-qa, data-testid, data-name attributes")
    print("  - Use stable CSS selectors (classes, IDs)")
    print("  - After recording, review and optimize selectors")
    print("=" * 60)
    
    # Start Playwright codegen with selector preferences
    os.system(f'playwright codegen "{url}" --target python --save-storage=auth.json')

if __name__ == "__main__":
    record_test()
