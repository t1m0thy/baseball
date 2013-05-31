import unittest
import logging
import manager
import gamecontainer
from constants import CONTAINER_PATH


TEST_GAME = 87568
TEST_GAME2 = 87259


class TestGameContainer(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 20000  # for TestCase assertEqual

    def test_scrape_vs_load(self):
        """
        test_events compare events coming from scraped game versus loaded game
        """
        scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster = manager.setup_scraper(TEST_GAME2)
        gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME2)

        scraper_events = []
        for scraper_half, gc_half in zip(scraper.halfs(), gc.halfs()):
            for scrape_raw_event, gc_info in zip(scraper_half.raw_events(), gc_half):
                self.assertEqual(scrape_raw_event.text(), gc_info["text"])

        self.assertEqual(away_starting_lineup, gc.away_lineup())
        self.assertEqual(home_starting_lineup, gc.home_lineup())
        self.assertEqual(away_roster, gc.away_roster())
        self.assertEqual(home_roster, gc.home_roster())

    def test_home_lineups(self):
        """
        test_load
        """

        html_game = manager.import_game(TEST_GAME, force_fresh=True)
        gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME)

        import pdb; pdb.set_trace()
        for jp, hp in zip(html_game.home_lineup, gc.home_lineup()):
            self.assertEqual(jp, hp)


    def test_lineups(self):
        parsed_gc = manager.scrape_to_container(TEST_GAME2)
        loaded_gc = gamecontainer.GameContainer(CONTAINER_PATH, TEST_GAME2)

        self.assertEqual(parsed_gc.home_lineup(), loaded_gc.home_lineup())
        self.assertEqual(parsed_gc.away_lineup(), loaded_gc.away_lineup())


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
        self.assertEqual(away_starting_lineup, self.gc.away_lineup())
        self.assertEqual(away_roster, self.gc.away_roster())

    def test_home(self):
        scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster = self.base_state
        self.assertEqual(home_starting_lineup, self.gc.home_lineup)
        self.assertEqual(home_roster, self.gc.home_roster)
