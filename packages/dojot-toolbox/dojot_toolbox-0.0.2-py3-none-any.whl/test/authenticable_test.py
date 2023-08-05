import sys
sys.path.append("..")

import unittest
from lib import Authenticable
from unittest.mock import patch

class AuthenticableTest(unittest.TestCase):

    def test_ask_username(self):
        with patch('builtins.input', return_value="anderson"):
            username = Authenticable().ask_username("What is your username", "dojot")
            self.assertEqual(username, "anderson") 

    def test_ask_username_when_is_empty(self):
        with patch('builtins.input', return_value=""):
            username = Authenticable().ask_username("What is your username", "dojot")
            self.assertEqual(username, "dojot")

    def test_ask_password(self):
        with patch('getpass.getpass', return_value="xxx"):
            password = Authenticable().ask_password("What is your username", "dojot")
            self.assertEqual(password, "xxx")

    def test_ask_password_when_is_empty(self):
        with patch('getpass.getpass', return_value=""):
            password = Authenticable().ask_password("What is your username", "dojot")
            self.assertEqual(password, "dojot")                                             

if __name__ == '__main__':
    unittest.main()