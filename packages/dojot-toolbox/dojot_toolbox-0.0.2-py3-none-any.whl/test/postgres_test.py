import sys
sys.path.append("..")

import unittest
from lib import Postgres
from unittest.mock import patch

class PostgresTest(unittest.TestCase):

    def setUp(self):
        self.postgres = Postgres()

    def test_ask_super_username(self):
        with patch('builtins.input', return_value="root"):
            vars = self.postgres.ask_super_username().vars
            self.assertEqual(vars['dojot_psql_super_user'], "root")

    def test_ask_super_username_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.postgres.ask_super_username().vars
            self.assertEqual(vars['dojot_psql_super_user'], "postgres")        

    def test_ask_super_password(self):
        with patch('getpass.getpass', return_value="root"):
            vars = self.postgres.and_super_password().vars
            self.assertEqual(vars['dojot_psql_super_passwd'], "root")  

    def test_ask_super_password_using_default(self):
        with patch('getpass.getpass', return_value=""):
            vars = self.postgres.and_super_password().vars
            self.assertEqual(vars['dojot_psql_super_passwd'], "postgres")        

    def test_ask_if_use_persistent_volume(self):
        with patch('builtins.input', return_value="y"):
            vars = self.postgres.and_if_use_persistent_volume().vars
            self.assertEqual(vars['dojot_psql_persistent_volumes'], True)

    def test_ask_if_use_persistent_volume_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.postgres.and_if_use_persistent_volume().vars
            self.assertEqual(vars['dojot_psql_persistent_volumes'], False)                    

    def test_ask_volume_size_when_use_volume(self):
        with patch('builtins.input', return_value="y"):
            self.postgres.and_if_use_persistent_volume().vars

        with patch('builtins.input', return_value="2"):
            vars = self.postgres.and_volume_size().vars
            self.assertEqual(vars['dojot_psql_volume_size'], 2)

    def test_ask_volume_size_when_not_use_volume(self):
        with patch('builtins.input', return_value="n"):
            self.postgres.and_if_use_persistent_volume().vars

        with patch('builtins.input', return_value="2"):
            vars = self.postgres.and_volume_size().vars
            self.assertEqual(vars['dojot_psql_volume_size'], 10)            

if __name__ == '__main__':
    unittest.main()