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
        self.game = gamestate.GameState()
        self.parser = psp.PointStreakParser(self.game, ["Collin Shaw"])
        self.test_game_id = "109440"

    # def test_cs(self):
    #     self.parser.parse_event("Ball, Ball, Ball, Called Strike, 19 Collin Shaw putout (caught stealing: CS ) for out number 3\n")

    def test_cs2(self):
        self.game._bases.advance('Collin Shaw', 1)
        self.parser.parse_event("Ball, Ball, Ball, Called Strike, 19 Collin Shaw putout (Caught Stealing: CS) for out number 3")
