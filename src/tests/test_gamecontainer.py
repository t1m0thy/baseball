import unittest

import logging
import manager
import gamecontainer
from constants import CONTAINER_PATH


TEST_GAME = 87568
TEST_GAME2 = 87259

class TestGameContainer(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 20000 # for TestCase assertEqual

    def test_load(self):
        """
        compare freshly made gamecontainer (from setUp) with one loaded from disk
        """
        parsed_gc = manager.scrape_to_container(TEST_GAME, save_container=False)
        loaded_gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME)

        for k, v in vars(parsed_gc).items():
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

    def test_twice(self):
        """
        compare freshly made gamecontainer (from setUp) with one loaded from disk
        """
        gc1 = gamecontainer.GameContainer(CONTAINER_PATH, 1)
        gc2 = gamecontainer.GameContainer(CONTAINER_PATH, 2)

        for h1, h2 in zip(gc1.halfs(), gc2.halfs()):
            for i1, i2 in zip(h1, h2):
                self.assertEqual(i1["text"], i2["text"])

        import pdb; pdb.set_trace()
        self.assertEqual(gc1.away_lineup, gc2.away_lineup)
        print gc1.away_lineup
        print gc2.away_lineup
        self.assertEqual(gc1.home_lineup, gc2.home_lineup)
        print gc1.home_lineup
        print gc2.home_lineup

        self.assertEqual(gc1.away_roster, gc2.away_roster)
        self.assertEqual(gc1.home_roster, gc2.home_roster)

    def test_events(self):
        """
        compare freshly made gamecontainer (from setUp) with one loaded from disk
        """
        scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster = manager.setup_scraper(TEST_GAME2)
        gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME2)

        scraper_events = []
        for scraper_half, gc_half in zip(scraper.halfs(), gc.halfs()):
            for scrape_raw_event, gc_info in zip(scraper_half.raw_events(), gc_half):
                self.assertEqual(scrape_raw_event.text(), gc_info["text"])


        self.assertEqual(away_starting_lineup, gc.away_lineup)
        self.assertEqual(home_starting_lineup, gc.home_lineup)
        self.assertEqual(away_roster, gc.away_roster)
        self.assertEqual(home_roster, gc.home_roster)

    def test_load2(self):
        """
        compare freshly made gamecontainer (from setUp) with one loaded from disk
        """

        html_game = manager.import_game(TEST_GAME, force_fresh=True)
        gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME)


        for jp, hp in zip(html_game.home_lineup, gc.home_lineup):
            self.assertEqual(jp, hp)

    def test_load3(self):
        parsed_gc = manager.scrape_to_container(TEST_GAME2)
        loaded_gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME2)

        self.assertEqual(parsed_gc.home_lineup, loaded_gc.home_lineup)
        self.assertEqual(parsed_gc.away_lineup, loaded_gc.away_lineup)

class TestParseEffect(unittest.TestCase):
    def setUp(self):
        self.base_state = manager.setup_scraper(TEST_GAME)
        self.gc = manager.scrape_to_container(TEST_GAME)
        manager.parse_from_container(self.gc)

    def test_events(self):
        scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster = self.base_state
        scraper_events = []
        for scraper_half, gc_half in zip(scraper.halfs(), self.gc.halfs()):
            for scrape_raw_event, gc_info in zip(scraper_half.raw_events(), gc_half):
                self.assertEqual(scrape_raw_event.text(), gc_info["text"])

    def test_away(self):
        scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster = self.base_state
        import pdb; pdb.set_trace()
        self.assertEqual(away_starting_lineup, self.gc.away_lineup)
        self.assertEqual(away_roster, self.gc.away_roster)

    def test_home(self):
        scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster = self.base_state
        self.assertEqual(home_starting_lineup, self.gc.home_lineup)
        self.assertEqual(home_roster, self.gc.home_roster)
