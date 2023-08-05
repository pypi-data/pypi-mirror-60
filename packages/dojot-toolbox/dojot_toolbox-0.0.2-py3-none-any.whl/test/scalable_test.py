import sys
sys.path.append("..")

import unittest
from lib import Scalable
from unittest.mock import patch

class ScalableTest(unittest.TestCase):

    def test_ask_replicas_for_user(self):
        with patch('builtins.input', return_value="2"):
            scalable = Scalable()
            res = scalable.ask_replicas(component="Cron", use=True)
            self.assertEqual(res, 2)

    def test_ask_replicas_for_user_with_default_value(self):
        with patch('builtins.input', return_value=""):
            scalable = Scalable()
            res = scalable.ask_replicas(component="Cron", use=True)
            self.assertEqual(res, 1)

    def test_ask_replicas_for_user_with_default_value_overrided(self):
        with patch('builtins.input', return_value=""):
            scalable = Scalable()
            res = scalable.ask_replicas(component="Cron", use=True, default=5)
            self.assertEqual(res, 5)        

    def test_ask_replicas_for_user_with_no_int_value(self):
        with patch('builtins.input', return_value="xxx"):
            scalable = Scalable()
            res = scalable.ask_replicas(component="Cron", use=True)
            self.assertEqual(res, 1) 

    def test_ask_replicas_for_user_when_component_is_not_used(self):
        scalable = Scalable()
        res = scalable.ask_replicas(component="Cron", use=False)
        self.assertEqual(res, 1)                       


if __name__ == '__main__':
    unittest.main()