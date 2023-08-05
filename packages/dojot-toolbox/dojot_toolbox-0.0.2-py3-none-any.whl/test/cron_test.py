import sys
sys.path.append("..")

import unittest
from lib import Cron

class CronTest(unittest.TestCase):

    def test_return_vars(self):
        cron = Cron()
        self.assertEqual(cron.vars['dojot_cron_use'], False)


if __name__ == '__main__':
    unittest.main()