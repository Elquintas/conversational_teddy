import unittest
from unittest.mock import patch
import os
import sys

if True:  # used to bypass flake8
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    )

from logic_manager import teddy_server_logic


class TestTeddyServerLogic(unittest.TestCase):

    def setUp(self):
        self.mock_data = {
            "intentions": {
                "no-understand": {"options": [{"file_path": "no_understand.wav"}]},
                "story": {"options": [{"file_path": "story.wav"}]},
                "joke": {"options": [{"file_path": "joke.wav"}]},
                "fact": {"options": [{"file_path": "fact.wav"}]},
                "riddle": {"options": [{"file_path": "riddle.wav"}]},
                "proverb": {"options": [{"file_path": "proverb.wav"}]},
                "tongue-twister": {"options": [{"file_path": "tonguetwister.wav"}]},
                "bye": {"options": [{"file_path": "bye.wav"}]},
            }
        }
        self.asr_model = None  # Mock ASR model, not used in logic

    def test_story_intent(self):
        self.assertEqual(
            teddy_server_logic("tell me a story", self.mock_data, self.asr_model),
            ("story.wav", "story"),
        )

    def test_joke_intent(self):
        self.assertEqual(
            teddy_server_logic("tell me a joke", self.mock_data, self.asr_model),
            ("joke.wav", "joke"),
        )

    def test_fact_intent(self):
        self.assertEqual(
            teddy_server_logic("give me a fact", self.mock_data, self.asr_model),
            ("fact.wav", "fact"),
        )

    def test_riddle_intent(self):
        self.assertEqual(
            teddy_server_logic("I want a riddle", self.mock_data, self.asr_model),
            ("riddle.wav", "riddle"),
        )

    def test_proverb_intent(self):
        self.assertEqual(
            teddy_server_logic("share a proverb", self.mock_data, self.asr_model),
            ("proverb.wav", "proverb"),
        )

    def test_tonguetwister_intent(self):
        self.assertEqual(
            teddy_server_logic(
                "give me a tongue twister", self.mock_data, self.asr_model
            ),
            ("tonguetwister.wav", "tonguetwister"),
        )

    def test_no_understand(self):
        self.assertEqual(
            teddy_server_logic("", self.mock_data, self.asr_model),
            ("no_understand.wav", "no-understand"),
        )

    @patch("game_manager.SpeechGameInterface.run")
    def test_game_intent(self, mock_game_run):
        self.assertEqual(
            teddy_server_logic("how do I escape", self.mock_data, self.asr_model),
            ("bye.wav", "bye"),
        )
        mock_game_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
