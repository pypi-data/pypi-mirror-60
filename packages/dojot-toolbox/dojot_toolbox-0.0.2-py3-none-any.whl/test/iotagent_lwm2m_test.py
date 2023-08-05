import sys
sys.path.append("..")

import unittest
from lib import IoTAgentLWM2M
from unittest.mock import patch

class IoTAgentLWM2MTest(unittest.TestCase):

    def setUp(self):
        self.iotagent = IoTAgentLWM2M()

    def test_ask_use(self):
        with patch('builtins.input', return_value="y"):
            vars = self.iotagent.ask_use().vars
            self.assertEqual(vars['dojot_iotagent_lwm2m_use'], True)

    def test_ask_use_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.iotagent.ask_use().vars
            self.assertEqual(vars['dojot_iotagent_lwm2m_use'], True)  


if __name__ == '__main__':
    unittest.main()