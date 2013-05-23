import unittest

import manager
import gamecontainer
from constants import CONTAINER_PATH


TEST_GAME = 87343
class TestGameContainer(unittest.TestCase):
    def setUp(self):
        self.gc = manager.scrape_to_container(TEST_GAME)
        self.maxDiff = 20000 # for TestCase assertEqual

    def test_load(self):
        """
        compare freshly made gamecontainer (from setUp) with one loaded from disk
        """
        loaded_gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME)

        for k, v in vars(self.gc).items():
            if k != "current_half": # current_half is not significant, it's just a read/write pointer
                print "Checking", k

                if type(v) == dict:
                    for ik, iv in v.items():
                        self.assertEqual(getattr(loaded_gc, k).get(ik), iv)
                if type(v) == list:
                    for i, item in enumerate(v):
                        self.assertEqual(getattr(loaded_gc, k)[i], item)
                else:
                    self.assertEqual(getattr(loaded_gc, k), v)
