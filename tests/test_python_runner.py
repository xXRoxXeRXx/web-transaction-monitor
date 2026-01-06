"""
Unit tests for python_runner.py
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from runners.python_runner import PythonRunner


class TestPythonRunner:
    """Test suite for PythonRunner class"""
    
    def test_init(self):
        """Test PythonRunner initialization"""
        runner = PythonRunner()
        assert runner is not None
    
    def test_has_monitor_base_class_true(self):
        """Test detection of MonitorBase subclass"""
        runner = PythonRunner()
        
        # Create a temporary file with MonitorBase class
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from monitor_base import MonitorBase

class TestMonitor(MonitorBase):
    def run(self):
        pass
""")
            temp_file = f.name
        
        try:
            result = runner._has_monitor_base_class(temp_file)
            assert result is True
        finally:
            os.unlink(temp_file)
    
    def test_has_monitor_base_class_false(self):
        """Test detection when no MonitorBase subclass exists"""
        runner = PythonRunner()
        
        # Create a temporary file without MonitorBase class
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
class RegularClass:
    def method(self):
        pass
""")
            temp_file = f.name
        
        try:
            result = runner._has_monitor_base_class(temp_file)
            assert result is False
        finally:
            os.unlink(temp_file)
    
    def test_has_monitor_base_class_invalid_syntax(self):
        """Test handling of files with syntax errors"""
        runner = PythonRunner()
        
        # Create a temporary file with invalid Python
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("this is not valid python @@@ ###")
            temp_file = f.name
        
        try:
            result = runner._has_monitor_base_class(temp_file)
            assert result is False  # Should return False on parse error
        finally:
            os.unlink(temp_file)
    
    @patch('runners.python_runner.importlib.util.spec_from_file_location')
    @patch('runners.python_runner.importlib.util.module_from_spec')
    def test_run_class(self, mock_module_from_spec, mock_spec_from_file):
        """Test running a MonitorBase class"""
        runner = PythonRunner()
        
        # Mock the module loading
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module
        
        # Create a mock MonitorBase subclass
        from monitor_base import MonitorBase
        
        class MockMonitor(MonitorBase):
            def run(self):
                pass
        
        mock_monitor_instance = MagicMock()
        mock_monitor_class = MagicMock(return_value=mock_monitor_instance)
        
        # Set up module dict to return our mock class
        mock_module.__dict__ = {
            'MockMonitor': mock_monitor_class,
            '__builtins__': {},
        }
        
        # Make isinstance and issubclass work
        with patch('runners.python_runner.isinstance', return_value=True), \
             patch('runners.python_runner.issubclass', return_value=True):
            
            runner._run_class('/fake/path.py', 'test_usecase')
            
            # Verify spec was created and module loaded
            mock_spec_from_file.assert_called_once()
    
    @patch('runners.python_runner.subprocess.run')
    @patch('runners.python_runner.sys.executable', '/usr/bin/python')
    def test_run_script_success(self, mock_subprocess_run):
        """Test running a script successfully"""
        runner = PythonRunner()
        
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Script output"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        runner._run_script('/fake/script.py', 'test_script')
        
        # Verify subprocess was called
        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0][0] == '/usr/bin/python'
        assert call_args[0][0][1] == '/fake/script.py'
    
    @patch('runners.python_runner.subprocess.run')
    def test_run_script_failure(self, mock_subprocess_run):
        """Test handling of script execution failure"""
        runner = PythonRunner()
        
        # Mock failed subprocess execution
        from subprocess import CalledProcessError
        mock_subprocess_run.side_effect = CalledProcessError(
            returncode=1,
            cmd=['python', 'script.py'],
            stderr="Error message"
        )
        
        # Should not raise, just log the error
        runner._run_script('/fake/script.py', 'test_script')
        
        mock_subprocess_run.assert_called_once()
    
    @patch.object(PythonRunner, '_has_monitor_base_class')
    @patch.object(PythonRunner, '_run_class')
    def test_run_with_monitor_class(self, mock_run_class, mock_has_class):
        """Test run method when file contains MonitorBase class"""
        runner = PythonRunner()
        mock_has_class.return_value = True
        
        runner.run('/fake/file.py', 'test_case')
        
        mock_has_class.assert_called_once_with('/fake/file.py')
        mock_run_class.assert_called_once_with('/fake/file.py', 'test_case')
    
    @patch.object(PythonRunner, '_has_monitor_base_class')
    @patch.object(PythonRunner, '_run_script')
    def test_run_with_script(self, mock_run_script, mock_has_class):
        """Test run method when file is a regular script"""
        runner = PythonRunner()
        mock_has_class.return_value = False
        
        runner.run('/fake/script.py', 'test_script')
        
        mock_has_class.assert_called_once_with('/fake/script.py')
        mock_run_script.assert_called_once_with('/fake/script.py', 'test_script')
    
    @patch.object(PythonRunner, '_has_monitor_base_class')
    def test_run_with_exception(self, mock_has_class):
        """Test run method handles exceptions gracefully"""
        runner = PythonRunner()
        mock_has_class.side_effect = Exception("Unexpected error")
        
        # Should not raise, just log
        runner.run('/fake/file.py', 'test_case')
        
        mock_has_class.assert_called_once()


class TestPythonRunnerIntegration:
    """Integration tests with actual file execution"""
    
    def test_run_real_monitor_class(self):
        """Test running an actual MonitorBase implementation"""
        runner = PythonRunner()
        
        # Create a real test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from monitor_base import MonitorBase

class TestMonitor(MonitorBase):
    def run(self):
        # Minimal test - just verify it runs
        pass
""")
            temp_file = f.name
        
        try:
            # This should detect and attempt to run the class
            # We mock Playwright to avoid actual browser launch
            with patch('monitor_base.sync_playwright'):
                runner.run(temp_file, 'integration_test')
        finally:
            os.unlink(temp_file)
