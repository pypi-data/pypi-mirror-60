import sys
sys.path.append("..")

import unittest
import os
from lib import DojotCLI, Component, Gui, Cron
from unittest.mock import MagicMock, patch
from pathlib import Path


class DojotCLITest(unittest.TestCase):

    def test_should_configure(self):
        argv = ['main.py', 'configure']
        installer = DojotCLI(argv)
        self.assertTrue(installer.should_configure())

    # def test_create_vars_file_from_services(self):
    #     installer = Installer([])
    #     installer.create_vars_file_from([Gui(), Cron()])

    #     self.assertEqual(self.read_file(), "cron_replicas: 1\ngui_replicas: 1\nuse_cron: false\nuse_gui: false\n")

    # def test_create_vars_file_when_there_is_only_one_service(self):
    #     installer = Installer([])
    #     installer.create_vars_file_from([Gui()])

    #     self.assertEqual(self.read_file(), "gui_replicas: 1\nuse_gui: false\n")    

    # def test_create_vars_file_when_there_are_no_services(self):
    #     installer = Installer([])
    #     installer.create_vars_file_from([])

    #     self.assertEqual(self.read_file(), "") 

    # def test_create_vars_file_when_there_is_no_array(self):
    #     installer = Installer([])
    #     self.assertRaises(installer.create_vars_file_from("xxx"), ValueError)        


if __name__ == '__main__':
    unittest.main()