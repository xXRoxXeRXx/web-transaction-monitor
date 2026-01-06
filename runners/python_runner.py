import ast
import os
import time
import subprocess
import importlib.util
import sys
import logging
from typing import Optional
from monitor_base import MonitorBase, TRANS_DURATION, TRANS_SUCCESS, TRANS_LAST_RUN

logger = logging.getLogger(__name__)

class PythonRunner:
    def __init__(self) -> None:
        pass

    def run(self, file_path: str, usecase_name: Optional[str] = None) -> None:
        """
        Determines if the file contains a MonitorBase subclass or is a raw script,
        and executes it accordingly.
        """
        try:
            if self._has_monitor_base_class(file_path):
                self._run_class(file_path, usecase_name)
            else:
                self._run_script(file_path, usecase_name)
        except Exception:
            logger.exception(f"Error executing {file_path}")
            # Set metrics for top-level errors
            actual_name = usecase_name or os.path.basename(file_path).replace('.py', '')
            TRANS_SUCCESS.labels(usecase=actual_name).set(0)
            TRANS_LAST_RUN.labels(usecase=actual_name).set_to_current_time()

    def _has_monitor_base_class(self, file_path: str) -> bool:
        """
        Parses the file using AST to check for a class inheriting from MonitorBase without importing it.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
            
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'MonitorBase':
                            return True
            return False
        except Exception:
            return False

    def _run_class(self, file_path: str, usecase_name: Optional[str] = None) -> None:
        """
        Imports the module and instantiates/runs the MonitorBase subclass.
        """
        # Module name must be unique to avoid collisions in sys.modules
        # We use the usecase_name if provided, otherwise the filename
        module_name = usecase_name.replace('.', '_').replace('-', '_') if usecase_name else os.path.basename(file_path).replace('.py', '')
        
        # Ensure we don't conflict with existing modules if re-running
        if module_name in sys.modules:
            del sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find and run subclasses
        found = False
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, MonitorBase) and obj is not MonitorBase:
                logger.info(f"Running Class-Based Monitor: {name}")
                monitor = obj()
                if usecase_name:
                    monitor.usecase_name = usecase_name
                monitor.execute()
                found = True
        
        if not found:
            logger.warning(f"No MonitorBase subclass found in {file_path} despite detection.")

    def _run_script(self, file_path: str, usecase_name: Optional[str] = None) -> None:
        """
        Runs the file as a subprocess.
        """
        name = os.path.basename(file_path).replace('.py', '')
        # Fallback if no name provided
        actual_name = usecase_name if usecase_name else f"script_{name}"
        
        logger.info(f"Running Script-Based Monitor: {actual_name}")
        
        TRANS_LAST_RUN.labels(usecase=actual_name).set_to_current_time()
        start_time = time.time()
        success = False
        
        try:
            # Run python with the file
            # Ensure cwd is project root handling imports correctly
            env = os.environ.copy()
            project_root = os.getcwd()
            env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
            
            result = subprocess.run(
                [sys.executable, file_path],
                cwd=project_root,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            success = True
            duration = time.time() - start_time
            # For scripts, we can't easily capture step metrics unless they report them.
            # Assuming full execution is one step for now unless we parse output.
            TRANS_DURATION.labels(usecase=actual_name, step="full_execution").set(duration)
            logger.info(f"[{actual_name}] Success ({duration:.2f}s)")
            
        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"[{actual_name}] Failed: {e.stderr}")
            # We can log stdout too if needed
            if e.stdout:
                logger.debug(f"[{actual_name}] Output: {e.stdout}")
        except Exception as e:
            logger.error(f"[{actual_name}] Execution error: {e}")
        finally:
            TRANS_SUCCESS.labels(usecase=actual_name).set(1 if success else 0)
