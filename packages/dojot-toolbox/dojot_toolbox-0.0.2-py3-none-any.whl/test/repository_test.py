import sys
sys.path.append("..")

import unittest
from lib import Repository
from unittest.mock import patch

class RepositoryTest(unittest.TestCase):

    def test_ask_use_existent_repo_when_answer_is_yes(self):
        with patch('builtins.input', return_value="y"):
            repo = Repository()
            self.assertTrue(repo.ask_use_existent_repo())

    def test_ask_use_existent_repo_when_answer_is_other(self):
        with patch('builtins.input', return_value="n"):
            repo = Repository()
            self.assertFalse(repo.ask_use_existent_repo())        

    def test_ask_use_when_answer_is_empty(self):
        with patch('builtins.input', return_value=""):
            repo = Repository()
            self.assertFalse(repo.ask_use_existent_repo())


if __name__ == '__main__':
    unittest.main()