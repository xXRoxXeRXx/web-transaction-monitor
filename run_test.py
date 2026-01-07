#!/usr/bin/env python3
"""
Universal test runner for local execution with visible browser.

Usage:
    python run_test.py hidrive-legacy               # Run HiDrive Legacy Picture Test
    python run_test.py hidrive-legacy-settings      # Run HiDrive Legacy Settings Test
    python run_test.py hidrive-next                 # Run HiDrive Next Picture Test
    python run_test.py hidrive-next-settings        # Run HiDrive Next Settings Test
    python run_test.py nextcloud-workspace          # Run Nextcloud Workspace Picture Test
    python run_test.py nextcloud-workspace-settings # Run Nextcloud Workspace Settings Test
    python run_test.py nextcloud-workspace-document # Run Nextcloud Workspace Document Test
    python run_test.py managed-nextcloud            # Run IONOS Managed Nextcloud Picture Test
    python run_test.py managed-nextcloud-settings   # Run IONOS Managed Nextcloud Settings Test
    python run_test.py managed-nextcloud-document   # Run IONOS Managed Nextcloud Document Test
    python run_test.py all                          # Run all tests sequentially
"""
import sys
import os
from pathlib import Path
import importlib.util
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = project_root / '.env'
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✓ Loaded environment variables from .env file")
    else:
        print("⚠ Warning: .env file not found. Using default values.")

load_env_file()

# Test configuration: test_id -> (directory, file, class_name)
# Environment variables are read from .env file
TESTS = {
    'hidrive-legacy': {
        'dir': 'hidrive-legacy',
        'file': 'picture_test.py',
        'class': 'HiDriveLegacyPictureTest',
    },
    'hidrive-legacy-settings': {
        'dir': 'hidrive-legacy',
        'file': 'settings_test.py',
        'class': 'HiDriveLegacySettingsTest',
    },
    'hidrive-next': {
        'dir': 'hidrive-next',
        'file': 'picture_test.py',
        'class': 'HiDriveNextPictureTest',
    },
    'hidrive-next-settings': {
        'dir': 'hidrive-next',
        'file': 'settings_test.py',
        'class': 'HiDriveNextSettingsTest',
    },
    'nextcloud-workspace': {
        'dir': 'ionos-nextcloud-workspace',
        'file': 'picture_test.py',
        'class': 'IonosNextcloudWorkspacePictureTest',
    },
    'nextcloud-workspace-settings': {
        'dir': 'ionos-nextcloud-workspace',
        'file': 'settings_test.py',
        'class': 'IonosNextcloudWorkspaceSettingsTest',
    },
    'nextcloud-workspace-document': {
        'dir': 'ionos-nextcloud-workspace',
        'file': 'document_test.py',
        'class': 'IonosNextcloudWorkspaceDocumentTest',
    },
    'managed-nextcloud': {
        'dir': 'ionos-managed-nextcloud',
        'file': 'picture_test.py',
        'class': 'IonosManagedNextcloudPictureTest',
    },
    'managed-nextcloud-settings': {
        'dir': 'ionos-managed-nextcloud',
        'file': 'settings_test.py',
        'class': 'IonosManagedNextcloudSettingsTest',
    },
    'managed-nextcloud-document': {
        'dir': 'ionos-managed-nextcloud',
        'file': 'document_test.py',
        'class': 'IonosManagedNextcloudDocumentTest',
    }
}

def run_test(test_id: str, headless: bool = False) -> bool:
    """Run a single test by test_id. Returns True on success, False on failure."""
    if test_id not in TESTS:
        print(f"❌ Unknown test: {test_id}")
        print(f"Available tests: {', '.join(TESTS.keys())}")
        return False
    
    config = TESTS[test_id]
    
    # Set HEADLESS for local testing (override .env value)
    os.environ['HEADLESS'] = 'true' if headless else 'false'
    
    # Load test module
    test_file = project_root / "transactions" / config['dir'] / config['file']
    spec = importlib.util.spec_from_file_location(config['class'], test_file)
    test_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_module)
    
    # Run test
    print(f"\n{'='*60}")
    print(f"Running: {test_id}")
    print(f"Test: {config['class']}")
    print(f"Browser will open in visible mode")
    print('='*60)
    
    test_class = getattr(test_module, config['class'])
    test = test_class()
    
    try:
        test.execute()
        print('='*60)
        print(f"✅ {test_id} completed successfully!")
        print('='*60)
        return True
    except Exception as e:
        print('='*60)
        print(f"❌ {test_id} failed: {type(e).__name__}: {e}")
        print('='*60)
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print(f"\nAvailable tests:")
        for test_id in TESTS.keys():
            print(f"  - {test_id}")
        sys.exit(1)
    
    test_id = sys.argv[1]
    
    if test_id == 'all':
        print(f"\n🚀 Running all {len(TESTS)} tests sequentially...\n")
        results = {}
        for tid in TESTS.keys():
            results[tid] = run_test(tid)
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print('='*60)
        for tid, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} - {tid}")
        print('='*60)
        
        failed_count = sum(1 for success in results.values() if not success)
        if failed_count > 0:
            print(f"\n❌ {failed_count} test(s) failed")
            sys.exit(1)
        else:
            print(f"\n✅ All {len(results)} tests passed!")
    else:
        success = run_test(test_id)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
