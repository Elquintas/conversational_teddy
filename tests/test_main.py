import unittest
from unittest.mock import patch, mock_open, MagicMock
import numpy as np
import os
import sys

if True:  # used to bypass flake8
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    )

from main import load_config, callback, shared_state


class TestMainScript(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    @patch("yaml.safe_load", return_value={"key": "value"})
    def test_load_config(self, mock_yaml, mock_file):
        """Test loading YAML configuration."""
        config = load_config("dummy_path.yaml")
        self.assertEqual(config, {"key": "value"})
        mock_file.assert_called_once_with("dummy_path.yaml", "r")
        mock_yaml.assert_called_once()

    @patch("numpy.frombuffer", return_value=np.array([0, 1, 2, 3]))
    def test_callback_no_speech_detected(self, mock_frombuffer):
        """Test callback function when no speech is detected."""
        vad_mock = MagicMock()
        mbn_mock = MagicMock()
        vad_mock.transcribe.return_value = []
        mbn_mock.transcribe.return_value = ["unknown"]

        result = callback(b"dummy_data", 1024, None, None, vad_mock, mbn_mock, 0.5)
        self.assertEqual(result[1], 0)  # paContinue

    @patch("numpy.frombuffer", return_value=np.array([0, 1, 2, 3]))
    def test_callback_keyword_detected(self, mock_frombuffer):
        """Test callback function when a keyword is detected."""
        vad_mock = MagicMock()
        mbn_mock = MagicMock()
        vad_mock.transcribe.return_value = [
            0,
            0,
            0,
            0.6,
        ]  # Simulate VAD detecting speech
        mbn_mock.transcribe.return_value = ["marvin"]

        result = callback(b"dummy_data", 1024, None, None, vad_mock, mbn_mock, 0.5)
        self.assertEqual(result[1], 2)  # paAbort

    @patch("numpy.frombuffer", return_value=np.array([0, 1, 2, 3]))
    def test_callback_exit_condition(self, mock_frombuffer):
        """Test callback function when the stop keyword is detected."""
        vad_mock = MagicMock()
        mbn_mock = MagicMock()
        vad_mock.transcribe.return_value = [0, 0, 0, 0.7]  # Above threshold
        mbn_mock.transcribe.return_value = ["stop"]

        result = callback(b"dummy_data", 1024, None, None, vad_mock, mbn_mock, 0.5)
        self.assertTrue(shared_state["exit_cond"])  # Ensures exit condition is set
        self.assertEqual(result[1], 2)  # paAbort


if __name__ == "__main__":
    unittest.main()
