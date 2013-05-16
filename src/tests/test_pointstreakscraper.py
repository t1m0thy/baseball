import unittest

import setuplogger
setuplogger.setupRootLogger(0)

import pointstreakscraper as pss
from workerconstants import PERSISTENT_FILE_PATH

# class Test109951(unittest.TestCase):
#     def setUp(self):
#         self.scraper = pss.PointStreakScraper(109951, PERSISTENT_FILE_PATH)

#     def test_build_lineup(self):
#         self.scraper._build_html_player_tables()
#         self.assertEquals(self.scraper._away_html_player_list.find_player_by_number(34).iddict.get("pointstreak"), '351689')

#     def test_home_team(self):
#         self.assertEquals("Wareham Gatemen", self.scraper.home_team())
#         self.assertEquals("Yarmouth-Dennis Red Sox", self.scraper.away_team())


class Test87621(unittest.TestCase):
    def setUp(self):
        self.scraper = pss.PointStreakScraper(87621, PERSISTENT_FILE_PATH)

    def test_lineup(self):
        away_roster, home_roster = self.scraper.game_rosters()
        print away_roster
        print
        print home_roster
        print

        away_starting_lineup, home_starting_lineup = self.scraper.starting_lineups(away_roster, home_roster)
        print away_starting_lineup
        print
        print home_starting_lineup

        for i in range(1,10):
            away_starting_lineup.find_player_by_order(i)

        for i in range(1,10):
            home_starting_lineup.find_player_by_order(i)
