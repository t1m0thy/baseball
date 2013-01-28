import unittest
import logging
import setuplogger
rootlogger = setuplogger.setupRootLogger(logging.INFO)

import webbrowser
import pyparsing as pp

import pointstreakparser as psp
import pointstreakscraper as pss
import gamestate

logger = logging.getLogger("main")


class TestCase(unittest.TestCase):
    def setUp(self):
        self.parser = psp.PointStreakParser()
        self.test_game_id = "109440"
  
    def test_game(self):
        try:
            raw_event = None
            # init scraper for this game id
            scraper = pss.PointStreakScraper(self.test_game_id)
            # create new game state
            game = gamestate.GameState()
            game.home_team_id = scraper.home_team()
            game.visiting_team = scraper.away_team()
            game.game_id = self.test_game_id

            self.parser.set_game(game)

            away_starting_lineup, home_starting_lineup = scraper.starting_lineups()
            game.set_away_lineup(away_starting_lineup)
            game.set_home_lineup(home_starting_lineup)
            away_roster, home_roster = scraper.game_rosters()
            game.set_away_roster(away_roster)
            game.set_home_roster(home_roster)

            #=======================================================================
            # Parse plays
            #=======================================================================

            for half in scraper.halfs():
                game.new_half()
                for raw_event in half.raw_events():
                    try:
                        if not raw_event.is_sub():
                            game.new_batter(raw_event.batter())
                        self.parser.parse_event(raw_event.text())
                    except pp.ParseException, pe:
                        logger.critical("%s: %s of inning %s\n%s" % (raw_event.title(),
                                                                      game.get_half_string(),
                                                                      game.inning,
                                                                      pe.markInputline()))
                        raise
                    except:
                        raise  # StandardError("Error with event: {}".format(raw_event.text()))
            game.set_previous_event_as_game_end()

        except Exception:
            logger.exception("Error in Game %s in %s of inning %s" % (game.game_id, game.get_half_string(), game.inning))
            if raw_event is not None:
                logger.error("possible source: {}".format(raw_event.text()))
            if raw_input("show_problem_page?") == 'y':
                webbrowser.open_new_tab(scraper.review_url())
            raise
        