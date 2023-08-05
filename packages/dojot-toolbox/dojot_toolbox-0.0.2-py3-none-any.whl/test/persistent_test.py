import sys
sys.path.append("..")

import unittest
from lib import Persistent
from unittest.mock import patch

class PersistentTest(unittest.TestCase):

    def test_ask_persistence_when_answer_is_yes(self):
        with patch('builtins.input', return_value="y"):
            persistent = Persistent()
            self.assertTrue(persistent.ask_persistence_volume("cron"))

    def test_ask_persistence_when_answer_is_other(self):
        with patch('builtins.input', return_value="n"):
            persistent = Persistent()
            self.assertFalse(persistent.ask_persistence_volume("cron"))        

    def test_ask_persistence_when_answer_is_empty(self):
        with patch('builtins.input', return_value=""):
            persistent = Persistent()
            self.assertFalse(persistent.ask_persistence_volume("cron"))

    def test_ask_volume_size(self):
        with patch('builtins.input', return_value="222"):
            persistent = Persistent()
            res = persistent.ask_volume_size(use=True, component="cron")
            self.assertEqual(res, 222)          


if __name__ == '__main__':
    unittest.main()