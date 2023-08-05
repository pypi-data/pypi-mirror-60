import sys
sys.path.append("..")

import unittest
from lib import K8sCLI
from unittest.mock import patch

class K8sCliTest(unittest.TestCase):

    def setUp(self):
        self.k8s = K8sCLI()

    def test_is_installed(self):
        self.assertTrue(self.k8s.is_installed())


if __name__ == '__main__':
    unittest.main()