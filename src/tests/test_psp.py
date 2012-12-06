import lineup
from lineup import Player
from constants import LEFT, RIGHT
import unittest
import pointstreakparser as psp

class TestCase(unittest.TestCase):
    def setUp(self):


    def test_popup(self):
        psp.popup.parseString("P3F")
