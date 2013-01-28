import lineup
from lineup import Player, LineupError
from constants import LEFT, RIGHT
import unittest


class TestCase(unittest.TestCase):
    def setUp(self):
        self.lineup = lineup.Lineup()

    def test_move(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.move_player("Wade Boggs", "LF")
        self.assertEqual(self.lineup.find_player_by_position("LF").name, "Wade Boggs")

    def test_remove(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.remove_player("Wade Boggs")
        self.assertRaises(KeyError, self.lineup.find_player_by_name, ("Wade Boggs",))

    def test_incomplete(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.assertFalse(self.lineup.is_complete())

        self.lineup.add_player(Player("Dwight Evans", 24, 2, "RF", RIGHT))
        self.lineup.add_player(Player("Jim Rice", 14, 3, "LF", RIGHT))
        self.lineup.add_player(Player("Mike Easler", 7, 4, "DH", LEFT))
        self.lineup.add_player(Player("Tony Armas", 20, 5, "CF", RIGHT))
        self.lineup.add_player(Player("Bill Buckner", 6, 6, "1B", LEFT))
        self.lineup.add_player(Player("Rich Gedman", 10, 7, "C", LEFT))
        self.lineup.add_player(Player("Marty Barret", 17, 8, "2B", RIGHT))
        self.lineup.add_player(Player("Jackie Gutierrez", 41, 9, "SS", RIGHT))
        self.assertFalse(self.lineup.is_complete())
        self.assertRaises(LineupError, self.lineup.is_complete, raise_reason=True)

    def test_update(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "P", LEFT))
        self.lineup.update_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.assertEqual(self.lineup.find_player_by_position("3B").name, "Wade Boggs")
        pass

    def test_update_error(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "P", LEFT))
        self.lineup.update_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.assertRaises(KeyError, self.lineup.update_player, Player("Wade Boggs", None, 1, "3B", LEFT))
        pass

class TestCaseComplete(unittest.TestCase):
    def setUp(self):
        self.lineup = lineup.Lineup()
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.add_player(Player("Dwight Evans", 24, 2, "RF", RIGHT))
        self.lineup.add_player(Player("Jim Rice", 14, 3, "LF", RIGHT))
        self.lineup.add_player(Player("Mike Easler", 7, 4, "DH", LEFT))
        self.lineup.add_player(Player("Tony Armas", 20, 5, "CF", RIGHT))
        self.lineup.add_player(Player("Bill Buckner", 6, 6, "1B", LEFT))
        self.lineup.add_player(Player("Rich Gedman", 10, 7, "C", LEFT))
        self.lineup.add_player(Player("Marty Barret", 17, 8, "2B", RIGHT))
        self.lineup.add_player(Player("Jackie Gutierrez", 41, 9, "SS", RIGHT))
        self.lineup.add_player(Player("Oil Can Boyd", 41, 10, "P", RIGHT))

    def test_complete(self):
        self.assertTrue(self.lineup.is_complete(raise_reason=True))

    def test_lookups(self):
        self.assertEqual("Marty Barret", self.lineup.find_player_by_order(8).name)
        self.assertEqual("Marty Barret", self.lineup.find_player_by_position("2B").name)
        self.assertEqual("2B", self.lineup.find_player_by_name("Marty Barret").position)
        self.assertEqual(8, self.lineup.find_player_by_position("2B").order)

    def test_move(self):
        self.lineup.move_player("Jim Rice", "DH")
        self.assertFalse(self.lineup.is_complete())

    def test_missing_postiton(self):
        self.lineup.move_player("Jim Rice", "DH")
        self.assertRaises(KeyError, self.lineup.find_player_by_position, "LF")

    def test_bad_order(self):
        self.assertRaises(KeyError, self.lineup.find_player_by_order, 12)

    def test_double_add(self):
        self.assertRaises(LineupError, self.lineup.add_player, Player("Oil Can Boyd", 41, 10, "P", RIGHT))

    def test_print(self):
        print self.lineup