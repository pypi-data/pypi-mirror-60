import sys
sys.path.append("..")

import unittest
from lib import Auth
from unittest.mock import patch

class AuthTest(unittest.TestCase):

    def setUp(self):
        self.auth = Auth()

    def test_ask_pg_username(self):
        with patch('builtins.input', return_value="root"):
            vars = self.auth.and_pg_username().vars
            self.assertEqual(vars['dojot_psql_auth_user'], "root")

    def test_ask_pg_username_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.auth.and_pg_username().vars
            self.assertEqual(vars['dojot_psql_auth_user'], "auth")        

    def test_ask_pg_password(self):
        with patch('getpass.getpass', return_value="root"):
            vars = self.auth.and_pg_password().vars
            self.assertEqual(vars['dojot_psql_auth_passwd'], "root")

    def test_ask_pg_password_using_default(self):
        with patch('getpass.getpass', return_value=""):
            vars = self.auth.and_pg_password().vars
            self.assertEqual(vars['dojot_psql_auth_passwd'], "auth")        

    def test_ask_if_should_send_mail(self):
        with patch('builtins.input', return_value="y"):
            vars = self.auth.ask_if_should_send_mail().vars
            self.assertEqual(vars['dojot_auth_email_enabled'], True)

    def test_ask_if_should_send_mail_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.auth.ask_if_should_send_mail().vars
            self.assertEqual(vars['dojot_auth_email_enabled'], True)        

    def test_ask_smtp_host_where_use_email(self):
        with patch('builtins.input', return_value="y"):
            self.auth.ask_if_should_send_mail()

        with patch('builtins.input', return_value="localhost"):
            vars = self.auth.and_smtp_host().vars
            self.assertEqual(vars['dojot_auth_email_host'], "localhost")

    def test_ask_smtp_host_where_not_use_email(self):
        with patch('builtins.input', return_value="n"):
            self.auth.ask_if_should_send_mail()
            vars = self.auth.and_smtp_host().vars
            self.assertEqual(vars['dojot_auth_email_host'], "")

    def test_ask_smtp_username_where_use_email(self):
        with patch('builtins.input', return_value="y"):
            self.auth.ask_if_should_send_mail()

        with patch('builtins.input', return_value="root"):
            vars = self.auth.and_smtp_username().vars
            self.assertEqual(vars['dojot_auth_email_user'], "root")

    def test_ask_smtp_username_where_not_use_email(self):
        with patch('builtins.input', return_value="n"):
            self.auth.ask_if_should_send_mail()
            vars = self.auth.and_smtp_username().vars
            self.assertEqual(vars['dojot_auth_email_user'], "")

    def test_ask_smtp_password_where_use_email(self):
        with patch('builtins.input', return_value="y"):
            self.auth.ask_if_should_send_mail()

        with patch('getpass.getpass', return_value="root"):
            vars = self.auth.and_smtp_password().vars
            self.assertEqual(vars['dojot_auth_email_passwd'], "root")

    def test_ask_smtp_password_where_not_use_email(self):
        with patch('builtins.input', return_value="n"):
            self.auth.ask_if_should_send_mail()
            vars = self.auth.and_smtp_password().vars
            self.assertEqual(vars['dojot_auth_email_passwd'], "")

    def test_ask_password_reset_link_where_use_email(self):
        with patch('builtins.input', return_value="y"):
            self.auth.ask_if_should_send_mail()

        with patch('builtins.input', return_value="root"):
            vars = self.auth.and_password_reset_link().vars
            self.assertEqual(vars['dojot_auth_smtp_reset_link'], "root")

    def test_ask_password_reset_link_where_not_use_email(self):
        with patch('builtins.input', return_value="n"):
            self.auth.ask_if_should_send_mail()
            vars = self.auth.and_password_reset_link().vars
            self.assertEqual(vars['dojot_auth_smtp_reset_link'], "")                        



if __name__ == '__main__':
    unittest.main()