"""Tests for pyps4_2ndscreen.helpers."""
from unittest.mock import patch
from pyps4_2ndscreen import helpers

def test_has_devices():
    """Test has_devices calls."""
    with patch("helpers.Discovery", autospec=True) as mock_discovery:
        helper = helpers.Helper()
        helper.has_devices()
        mock_discovery.search.assert_called_once()

