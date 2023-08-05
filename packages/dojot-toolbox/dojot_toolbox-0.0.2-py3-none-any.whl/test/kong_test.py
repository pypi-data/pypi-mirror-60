import sys
sys.path.append("..")

import unittest
from lib import Kong
from unittest.mock import patch

class KongTest(unittest.TestCase):

    def setUp(self):
        self.kong = Kong()

    def test_ask_req_per_minute(self):
        with patch('builtins.input', return_value="3"):
            vars = self.kong.ask_req_per_minute().vars
            self.assertEqual(vars['dojot_kong_req_per_minute'], 3)    

    def test_ask_req_per_minute_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.kong.ask_req_per_minute().vars
            self.assertEqual(vars['dojot_kong_req_per_minute'], 5)

    def test_ask_req_per_hour(self):
        with patch('builtins.input', return_value="3"):
            vars = self.kong.ask_req_per_hour().vars
            self.assertEqual(vars['dojot_kong_req_per_hour'], 3)    

    def test_ask_req_per_hour_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.kong.ask_req_per_hour().vars
            self.assertEqual(vars['dojot_kong_req_per_hour'], 40)        

    def test_ask_pg_username(self):
        with patch('builtins.input', return_value="root"):
            vars = self.kong.ask_pg_username().vars
            self.assertEqual(vars['dojot_psql_kong_user'], "root")    

    def test_ask_pg_username_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.kong.ask_pg_username().vars
            self.assertEqual(vars['dojot_psql_kong_user'], "kong") 

    def test_ask_pg_password(self):
        with patch('getpass.getpass', return_value="root"):
            vars = self.kong.ask_pg_password().vars
            self.assertEqual(vars['dojot_psql_kong_passwd'], "root")    

    def test_ask_pg_passord_using_default(self):
        with patch('getpass.getpass', return_value=""):
            vars = self.kong.ask_pg_password().vars
            self.assertEqual(vars['dojot_psql_kong_passwd'], "kong")               


if __name__ == '__main__':
    unittest.main()