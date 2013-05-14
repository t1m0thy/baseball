import lineup
from lineup import Player, LineupError, Name
from constants import LEFT, RIGHT
import unittest


class TestNames(unittest.TestCase):
    def test_equality1(self):
        a = Name("Hirzel, Tim")
        b = Name("Tim Hirzel")
        self.assertTrue(a == b)

    def test_equality2(self):
        a = Name("Hirzel, Tim")
        a.set_id("hirzt001")
        b = "hirzt001"
        self.assertTrue(a == b)

    def test_equality3(self):
        a = Name("Hirzel, Tim")
        b = "hirzt"
        self.assertTrue(a == b)

    def test_equality4(self):
        a = Name("Hirzel, Tim")
        b = Name("Bob Brown")
        self.assertNotEqual(a.last, b.last)


class TestPlayer(unittest.TestCase):
    def test_merge(self):
        boggs = Player("Wade Boggs", 26, 1, "P", LEFT)
        boggs2 = Player("Wade Boggs", 26, 1, "P", LEFT)
        self.assertEqual(boggs, boggs2)
        boggs2.number = None
        boggs.merge(boggs2)
        self.assertEqual(boggs.number, 26)

    def test_name_equals(self):
        boggs = Player("Wade Boggs", 26, 1, "P", LEFT)
        self.assertEquals(boggs.name, "wade boggs ")

    def test_name_not_equals(self):
        boggs = Player("Wade Boggs JR", 26, 1, "P", LEFT)
        self.assertFalse(boggs.name != "wade boggs jr")
        self.assertTrue(boggs.name == "wade boggs jr")


class TestLineup(unittest.TestCase):
    def setUp(self):
        self.lineup = lineup.Lineup()

    def test_move(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.move_player("Wade Boggs", "LF")
        self.assertEqual(self.lineup.find_player_by_position("LF").name, "Wade Boggs")

    def test_remove(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.remove_player("Wade Boggs")
        self.assertRaises(KeyError, self.lineup.find_player_by_name, "Wade Boggs")

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

    def test_complete(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.add_player(Player("Dwight Evans", 24, 2, "RF", RIGHT))
        self.lineup.add_player(Player("Jim Rice", 14, 3, "LF", RIGHT))
        self.lineup.add_player(Player("Mike Easler", 22, 4, "DH", LEFT))
        self.lineup.add_player(Player("Tony Armas", 20, 5, "CF", RIGHT))
        self.lineup.add_player(Player("Bill Buckner", 6, 6, "1B", LEFT))
        self.lineup.add_player(Player("Rich Gedman", 10, 7, "C", LEFT))
        self.lineup.add_player(Player("Marty Barret", 17, 8, "2B", RIGHT))
        self.lineup.add_player(Player("Jackie Gutierrez", 41, 9, "SS", RIGHT))
        self.lineup.add_player(Player("Oil Can Boyd", 41, 10, "P", RIGHT))
        self.assertTrue(self.lineup.is_complete())

    def test_update(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "P", LEFT))
        self.lineup.update_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.assertEqual(self.lineup.find_player_by_position("3B").name, "Wade Boggs")

    def test_update_position(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.update_position(Player("Big Bird", 26, 1, "3B", LEFT))
        self.assertEqual(self.lineup.find_player_by_position("3B").name, "Big Bird")

    def test_update_error(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "P", LEFT))
        self.lineup.update_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.assertRaises(StandardError, self.lineup.update_player, Player(None, 26, 1, "3B", LEFT))

    def test_update_to_add(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "P", LEFT))
        self.lineup.update_player(Player("Bill Buckner", 6, 6, "1B", LEFT))
        self.assertEquals(2, len(self.lineup))

    def test_find_by_position(self):
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.assertEquals("Wade Boggs", self.lineup.find_player_by_position("3B").name)


class TestCaseComplete(unittest.TestCase):
    def setUp(self):
        self.lineup = lineup.Lineup()
        self.lineup.add_player(Player("Wade Boggs", 26, 1, "3B", LEFT))
        self.lineup.add_player(Player("Dwight Evans", 24, 2, "RF", RIGHT))
        self.lineup.add_player(Player("Jim Rice", 14, 3, "LF", RIGHT))
        self.lineup.add_player(Player("Mike Easler", 'X', 4, "DH", LEFT))  # test numberless 'X'
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

    def test_closest_match(self):
        test = Player("Wade Boggs", None, 1, None, LEFT)
        result = test.find_closest_name(self.lineup)
        self.assertEqual(result, self.lineup.find_player_by_number(26))

    def test_closest_match2(self):
        test = Player("Boggs, W", None, None, None, None)
        result = test.find_closest_name(self.lineup)
        self.assertEqual(result, self.lineup.find_player_by_number(26))

#    def test_closest_match3(self):
#        test = Player(None, 26, None, None, None)
#        result = test.find_closest_name(self.lineup)
#        self.assertEqual(result, self.lineup.find_player_by_number(26))
#
#    def test_closest_match4(self):
#        test = Player(None, None, None, None, None)
#        self.assertRaises(ValueError, test.find_closest_name, self.lineup)
#
#    def test_closest_match5(self):
#        test = Player(None, None, None, None, LEFT)
#        self.assertRaises(ValueError, test.find_closest_name, self.lineup)
#
#    def test_closest_match6(self):
#        test = Player(None, None, None, "3B", None)
#        result = test.find_closest_name(self.lineup)
#        self.assertEqual(result, self.lineup.find_player_by_number(26))
