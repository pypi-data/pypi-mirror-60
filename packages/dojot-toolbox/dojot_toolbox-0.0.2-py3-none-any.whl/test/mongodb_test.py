import sys
sys.path.append("..")

import unittest
from lib import MongoDB
from unittest.mock import patch

class MongoDBTest(unittest.TestCase):

    def setUp(self):
        self.mongo = MongoDB()

    def test_ask_super_username(self):
        with patch('builtins.input', return_value="root"):
            vars = self.mongo.ask_super_username().vars
            self.assertEqual(vars['dojot_mongodb_super_user'], "root")

    def test_ask_super_username_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.mongo.ask_super_username().vars
            self.assertEqual(vars['dojot_mongodb_super_user'], "mongodb")        

    def test_ask_super_password(self):
        with patch('getpass.getpass', return_value="root"):
            vars = self.mongo.and_super_password().vars
            self.assertEqual(vars['dojot_mongodb_super_passwd'], "root")  

    def test_ask_super_password_using_default(self):
        with patch('getpass.getpass', return_value=""):
            vars = self.mongo.and_super_password().vars
            self.assertEqual(vars['dojot_mongodb_super_passwd'], "mongodb")  

    def test_ask_if_messages_will_be_persisted(self):
        with patch('builtins.input', return_value="n"):
            vars = self.mongo.and_if_messages_will_be_persisted().vars
            self.assertEqual(vars['dojot_persister_use'], False)

    def test_ask_if_messages_will_be_persisted_when_use_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.mongo.and_if_messages_will_be_persisted().vars
            self.assertEqual(vars['dojot_persister_use'], True)                

    def test_ask_persistence_time(self):
        with patch('builtins.input', return_value="25"):
            vars = self.mongo.and_persistence_time().vars
            self.assertEqual(vars['dojot_persister_persistence_time'], 25)  

    def test_ask_persistence_time_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.mongo.and_persistence_time().vars
            self.assertEqual(vars['dojot_persister_persistence_time'], 168)    

    def test_ask_persistence_time_when_messages_will_not_be_persisted(self):
        with patch('builtins.input', return_value="n"):
            self.mongo.and_if_messages_will_be_persisted()

        with patch('builtins.input', return_value="25"):
            vars = self.mongo.and_persistence_time().vars
            self.assertEqual(vars['dojot_persister_persistence_time'], 168)                    

    def test_ask_if_use_persistent_volume(self):
        with patch('builtins.input', return_value="y"):
            vars = self.mongo.and_if_use_persistent_volume().vars
            self.assertEqual(vars['dojot_mongodb_persistent_volumes'], True)

    def test_ask_if_use_persistent_volume_using_default(self):
        with patch('builtins.input', return_value=""):
            vars = self.mongo.and_if_use_persistent_volume().vars
            self.assertEqual(vars['dojot_mongodb_persistent_volumes'], False)

    def test_ask_if_use_persistent_volume_when_messages_will_not_be_persisted(self):
        with patch('builtins.input', return_value="n"):
            self.mongo.and_if_messages_will_be_persisted()

        with patch('builtins.input', return_value="y"):
            vars = self.mongo.and_if_use_persistent_volume().vars
            self.assertEqual(vars['dojot_mongodb_persistent_volumes'], False)                            

    def test_ask_volume_size_when_use_volume(self):
        with patch('builtins.input', return_value="y"):
            self.mongo.and_if_use_persistent_volume().vars

        with patch('builtins.input', return_value="2"):
            vars = self.mongo.and_volume_size().vars
            self.assertEqual(vars['dojot_mongodb_volume_size'], 2)

    def test_ask_volume_size_when_not_use_volume(self):
        with patch('builtins.input', return_value="n"):
            self.mongo.and_if_use_persistent_volume().vars

        with patch('builtins.input', return_value="2"):
            vars = self.mongo.and_volume_size().vars
            self.assertEqual(vars['dojot_mongodb_volume_size'], 10)  

    def test_ask_volume_size_when_messages_will_not_be_persisted(self):
        with patch('builtins.input', return_value="n"):
            self.mongo.and_if_messages_will_be_persisted()

        with patch('builtins.input', return_value="y"):
            self.mongo.and_if_use_persistent_volume().vars

        with patch('builtins.input', return_value="300"):
            vars = self.mongo.and_volume_size().vars
            self.assertEqual(vars['dojot_mongodb_volume_size'], 10)                  

if __name__ == '__main__':
    unittest.main()