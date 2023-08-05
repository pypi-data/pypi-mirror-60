import sys
sys.path.append("..")

import unittest
from lib import Optional
from unittest.mock import patch

class OptionalTest(unittest.TestCase):

    def test_ask_use_when_answer_is_yes(self):
        with patch('builtins.input', return_value="y"):
            optional = Optional()
            self.assertTrue(optional.ask_use("cron"))

    def test_ask_use_when_answer_is_no(self):
        with patch('builtins.input', return_value="n"):
            optional = Optional()
            self.assertFalse(optional.ask_use("cron")) 

    def test_ask_use_when_answer_is_other(self):
        with patch('builtins.input', return_value="xxx"):
            optional = Optional()
            self.assertTrue(optional.ask_use("cron", default=True))                

    def test_ask_use_when_answer_is_empty(self):
        with patch('builtins.input', return_value=""):
            optional = Optional()
            self.assertFalse(optional.ask_use("cron"))

    def test_ask_use_when_answer_default_is_set(self):
        with patch('builtins.input', return_value=""):
            optional = Optional()
            self.assertTrue(optional.ask_use("cron", default=True))        


if __name__ == '__main__':
    unittest.main()