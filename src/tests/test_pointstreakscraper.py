import unittest

import setuplogger
setuplogger.setupRootLogger(0)

import pointstreakscraper as pss


class Test109951(unittest.TestCase):
    def setUp(self):
        self.scraper = pss.PointStreakScraper("109951")

    def test_build_lineup(self):
        self.scraper._build_html_player_tables()
        self.assertEquals(self.scraper._away_html_player_list.find_player_by_number(34).iddict.get("pointstreak"), '351689')

    def test_home_team(self):
        self.assertEquals("Wareham Gatemen", self.scraper.home_team())
        self.assertEquals("Yarmouth-Dennis Red Sox", self.scraper.away_team())


class Test67703(unittest.TestCase):
    def setUp(self):
        self.scraper = pss.PointStreakScraper(67703)
        
    def test_lineup(self):
        away, home = self.scraper.scrape_lineup_from_seq_xml(0)
        
        
        self.scraper.starting_lineups()
        