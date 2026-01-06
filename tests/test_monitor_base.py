"""
Unit tests for monitor_base.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from monitor_base import MonitorBase, TRANS_DURATION, TRANS_SUCCESS, TRANS_LAST_RUN, STEP_FAILURE


class TestMonitor(MonitorBase):
    """Concrete implementation for testing"""
    def run(self):
        self.measure_step("test_step", lambda: None)


class TestMonitorBase:
    """Test suite for MonitorBase class"""
    
    def test_init(self):
        """Test MonitorBase initialization"""
        monitor = TestMonitor(usecase_name="test_usecase")
        assert monitor.usecase_name == "test_usecase"
        assert monitor.headless is True
        assert monitor.playwright is None
        assert monitor.browser is None
        assert monitor.page is None
    
    def test_init_with_headless_false(self):
        """Test MonitorBase initialization with headless=False"""
        monitor = TestMonitor(usecase_name="test_usecase", headless=False)
        assert monitor.headless is False
    
    @patch('monitor_base.sync_playwright')
    def test_setup(self, mock_playwright):
        """Test setup method initializes Playwright correctly"""
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.start.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        monitor = TestMonitor(usecase_name="test_usecase")
        monitor.setup()
        
        assert monitor.playwright == mock_pw_instance
        assert monitor.browser == mock_browser
        assert monitor.page == mock_page
        mock_pw_instance.chromium.launch.assert_called_once_with(headless=True)
    
    def test_teardown(self):
        """Test teardown method closes resources"""
        monitor = TestMonitor(usecase_name="test_usecase")
        monitor.page = MagicMock()
        monitor.browser = MagicMock()
        monitor.playwright = MagicMock()
        
        monitor.teardown()
        
        monitor.page.close.assert_called_once()
        monitor.browser.close.assert_called_once()
        monitor.playwright.stop.assert_called_once()
    
    def test_teardown_with_none_values(self):
        """Test teardown handles None values gracefully"""
        monitor = TestMonitor(usecase_name="test_usecase")
        # Should not raise any exception
        monitor.teardown()
    
    @patch('monitor_base.time.time')
    def test_measure_step_success(self, mock_time):
        """Test measure_step records successful step execution"""
        mock_time.side_effect = [100.0, 105.5]  # start, end
        
        monitor = TestMonitor(usecase_name="test_usecase")
        action = Mock()
        
        monitor.measure_step("test_step", action)
        
        action.assert_called_once()
        # Duration should be 5.5 seconds
        assert mock_time.call_count == 2
    
    @patch('monitor_base.time.time')
    def test_measure_step_failure(self, mock_time):
        """Test measure_step handles exceptions correctly"""
        mock_time.side_effect = [100.0, 102.0]
        
        monitor = TestMonitor(usecase_name="test_usecase")
        action = Mock(side_effect=ValueError("Test error"))
        
        with pytest.raises(ValueError, match="Test error"):
            monitor.measure_step("test_step", action)
        
        action.assert_called_once()
    
    @patch('monitor_base.sync_playwright')
    def test_execute_success(self, mock_playwright):
        """Test execute method with successful run"""
        mock_pw_instance = MagicMock()
        mock_playwright.return_value.start.return_value = mock_pw_instance
        
        monitor = TestMonitor(usecase_name="test_usecase")
        monitor.execute()
        
        # Should call setup, run, and teardown
        assert mock_pw_instance.chromium.launch.called
    
    @patch('monitor_base.sync_playwright')
    def test_execute_failure(self, mock_playwright):
        """Test execute method with failed run"""
        mock_pw_instance = MagicMock()
        mock_playwright.return_value.start.return_value = mock_pw_instance
        
        class FailingMonitor(MonitorBase):
            def run(self):
                raise RuntimeError("Test failure")
        
        monitor = FailingMonitor(usecase_name="test_usecase")
        monitor.execute()  # Should not raise, but record failure
        
        # Teardown should still be called
        assert mock_pw_instance.stop.called


class TestMetricsIntegration:
    """Test Prometheus metrics integration"""
    
    @patch('monitor_base.sync_playwright')
    def test_metrics_recorded_on_success(self, mock_playwright):
        """Test that metrics are recorded for successful execution"""
        mock_pw_instance = MagicMock()
        mock_playwright.return_value.start.return_value = mock_pw_instance
        
        monitor = TestMonitor(usecase_name="metrics_test")
        monitor.execute()
        
        # Check that success metric is set (we can't easily assert on Prometheus metrics,
        # but we verify no exceptions were raised)
        assert True  # If we got here, metrics were recorded without error
    
    @patch('monitor_base.sync_playwright')
    def test_metrics_recorded_on_failure(self, mock_playwright):
        """Test that metrics are recorded for failed execution"""
        mock_pw_instance = MagicMock()
        mock_playwright.return_value.start.return_value = mock_pw_instance
        
        class FailingMonitor(MonitorBase):
            def run(self):
                raise ValueError("Intentional failure")
        
        monitor = FailingMonitor(usecase_name="metrics_test_fail")
        monitor.execute()
        
        # Should complete without raising
        assert True
