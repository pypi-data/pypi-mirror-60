import sys
sys.path.append("..")

import unittest
from lib import Gui

class GuiTest(unittest.TestCase):

    def test_return_vars(self):
        gui = Gui()
        self.assertEqual(gui.vars['dojot_gui_use'], True)


if __name__ == '__main__':
    unittest.main()