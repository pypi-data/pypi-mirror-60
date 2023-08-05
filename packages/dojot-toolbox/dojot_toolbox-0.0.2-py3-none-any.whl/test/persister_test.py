import sys
sys.path.append("..")

import unittest
from lib import Persister
from unittest.mock import patch

class PersisterTest(unittest.TestCase):

    def setUp(self):
        self.persister = Persister()

    def test_ask_if_messages_will_be_persisted(self):
        with patch('builtins.input', return_value="n"):
            vars = self.persister.ask_if_messages_will_be_persisted().vars
            self.assertEqual(vars['dojot_persister_use'], False)

    def test_ask_if_messages_will_be_persisted_when_use_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.persister.ask_if_messages_will_be_persisted().vars
            self.assertEqual(vars['dojot_persister_use'], True)                

    def test_ask_persistence_time(self):
        with patch('builtins.input', return_value="25"):
            vars = self.persister.and_persistence_time().vars
            self.assertEqual(vars['dojot_persister_persistence_time'], 25)  

    def test_ask_persistence_time_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.persister.and_persistence_time().vars
            self.assertEqual(vars['dojot_persister_persistence_time'], 168)    


if __name__ == '__main__':
    unittest.main()