import unittest
import pointstreakscraper as pss


class TestCase(unittest.TestCase):
    def setUp(self):
        self.scraper = pss.PointStreakScraper("109951")

    def test_build_lineup(self):
        self.scraper._build_player_id_lookup_dict()
        self.assertEquals(self.scraper._away_playerid_by_num['34'], '351689')

    def test_home_team(self):
        self.assertEquals("Wareham Gatemen", self.scraper.home_team())
        self.assertEquals("Yarmouth-Dennis Red Sox", self.scraper.away_team())
