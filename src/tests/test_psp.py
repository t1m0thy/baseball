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

    def test_parse(self):
        self.parser.parse_event("Called Strike, Ball, Foul, Ball, 15 John Murphy advances to 1st (error by the third baseman)")

    def test_parse2(self):
        self.parser.parse_event("35 Ryan Donahue subs for Chris Matulis.")