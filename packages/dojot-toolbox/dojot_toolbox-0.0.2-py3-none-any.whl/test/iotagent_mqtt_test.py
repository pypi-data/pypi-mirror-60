import sys
sys.path.append("..")

import unittest
from lib import IoTAgentMQTT
from unittest.mock import patch

class IoTAgentMoscaTest(unittest.TestCase):

    def setUp(self):
        self.iotagent = IoTAgentMQTT()

    def test_ask_use(self):
        with patch('builtins.input', return_value="y"):
            vars = self.iotagent.ask_use().vars
            self.assertEqual(vars['dojot_iotagent_mosca_use'], True)

    def test_ask_use_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.iotagent.ask_use().vars
            self.assertEqual(vars['dojot_iotagent_mosca_use'], True)  

    def test_ask_replicas(self):
        with patch('builtins.input', return_value="10"):
            vars = self.iotagent.and_replicas().vars
            self.assertEqual(vars['dojot_iotagent_mosca_replicas'], 10) 

    def test_ask_replicas_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.iotagent.and_replicas().vars
            self.assertEqual(vars['dojot_iotagent_mosca_replicas'], 1)   

    def test_ask_replicas_when_will_not_be_used(self):
        with patch('builtins.input', return_value="n"):
            self.iotagent.ask_use().vars

        with patch('builtins.input', return_value="10"):
            vars = self.iotagent.and_replicas().vars
            self.assertEqual(vars['dojot_iotagent_mosca_replicas'], 1)        

    def test_ask_use_unsecured_mode(self):
        with patch('builtins.input', return_value="y"):
            vars = self.iotagent.and_use_insecure_mqtt().vars
            self.assertEqual(vars['dojot_insecure_mqtt'], 'true')

    def test_ask_use_unsecured_mode_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.iotagent.and_use_insecure_mqtt().vars
            self.assertEqual(vars['dojot_insecure_mqtt'], 'false')  

    def test_ask_use_unsecured_mode_when_will_not_be_used(self):
        with patch('builtins.input', return_value="n"):
            self.iotagent.ask_use().vars 

        with patch('builtins.input', return_value="y"):
            vars = self.iotagent.and_use_insecure_mqtt().vars
            self.assertEqual(vars['dojot_insecure_mqtt'], 'false')                                  


if __name__ == '__main__':
    unittest.main()