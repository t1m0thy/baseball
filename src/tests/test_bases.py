import unittest
import bases


class TestCase(unittest.TestCase):
    def setUp(self):
        self.bases = bases.Bases()

    def test_onbase(self):
        self.bases.advance("Bert", 3)
        self.assertEquals(self.bases.on_base(3), "Bert")

    def test_advance(self):
        self.bases.advance("Bert", 3)
        self.bases.advance("Ernie", 2)
        self.assertEquals(self.bases.runner_names(), (None, "Ernie", "Bert"))

    def test_force(self):
        self.bases.advance("Bert", 2)
        self.bases.advance("Ernie", 2)
        self.assertEquals(self.bases.force_runners(), [("Bert", 3)])

    def test_badbase(self):
        self.assertRaises(ValueError, self.bases.advance, player_name="Guy", base=7)

    def test_clear(self):
        self.bases.advance("Bert", 3)
        self.bases.advance("Ernie", 2)
        self.bases.advance("Oscar", 1)
        self.bases.clear()
        self.assertEquals(self.bases.runner_names(), (None, None, None))

    def test_valid(self):
        self.bases.advance("Bert", 3)
        self.bases.advance("Ernie", 3)
        self.assertFalse(self.bases.is_valid())
        self.bases.advance("Ernie", 4)
        self.assertTrue(self.bases.is_valid())

    def test_runner_count(self):
        self.bases.advance("Ernie", 3)
        self.assertEquals(self.bases.runner_count(), 1)
        self.bases.advance("Ernie", 4)
        self.assertEquals(self.bases.runner_count(), 0)

    def test_homerun(self):
        self.bases.advance("Ernie", 4)
        self.assertEquals(self.bases.runner_count(), 0)

    def test_return_strings(self):
        self.assertEquals("B-3", self.bases.advance("Bert", 3))
        self.assertEquals("B-2", self.bases.advance("Ernie", 2))
        self.assertEquals("B-1", self.bases.advance("Oscar", 1))

        self.assertEquals("3-H", self.bases.advance("Bert", 4))
        self.assertEquals("2-H", self.bases.advance("Ernie", 4))
        self.assertEquals("1-H", self.bases.advance("Oscar", 4))

        self.assertEquals("B-1", self.bases.advance("BigBird", 1))
        self.assertEquals("1-2", self.bases.advance("BigBird", 2))
        self.assertEquals("2-3", self.bases.advance("BigBird", 3))
        self.assertEquals("3-H", self.bases.advance("BigBird", 4))

        self.assertEquals(0, self.bases.runner_count())

    def test_pinch(self):
        self.bases.advance("Bert", 1)
        self.bases.replace_runner("Ernie", "Bert", 1)
        self.bases.advance("Ernie", 3)
        self.assertEquals(self.bases.on_base(3), "Ernie")

    def test_code(self):
        self.assertEquals(self.bases.code(), 0)
        self.bases.advance("Bert", 1)
        self.assertEquals(self.bases.code(), 1)
        self.bases.advance("Bert", 2)
        self.assertEquals(self.bases.code(), 2)
        self.bases.advance("Bert", 3)
        self.assertEquals(self.bases.code(), 4)
        self.bases.advance("Ernie", 1)
        self.assertEquals(self.bases.code(), 5)
        self.bases.advance("Ernie", 2)
        self.assertEquals(self.bases.code(), 6)
        self.bases.advance("Oscar", 1)
        self.assertEquals(self.bases.code(), 7)

    def test_fates(self):
        self.bases.advance("Bert", 1)
        berts_fate_id = self.bases.player_fate_id("Bert")
        self.bases.replace_runner("Ernie", "Bert", 1)
        self.bases.advance("Ernie", 3)
        self.assertEquals(self.bases.fate_for(berts_fate_id),3)

    def test_fates_2(self):
        self.bases.advance("Bert", 1)
        berts_fate_id_1 = self.bases.player_fate_id("Bert")
        self.bases.advance("Bert", 3)
        self.assertEquals(self.bases.fate_for(berts_fate_id_1),3)
        self.bases.advance("Bert", 5)
        self.assertEquals(self.bases.fate_for(berts_fate_id_1),5)

        self.bases.advance("Bert", 1)
        berts_fate_id_2 = self.bases.player_fate_id("Bert")
        self.assertEquals(self.bases.runners_fate_ids(), [berts_fate_id_2, 0, 0])
        self.assertEquals(len(self.bases.fates_id_lookup), 2)
        self.bases.advance("Bert", 3)
        self.assertEquals(self.bases.fate_for(berts_fate_id_2),3)
        self.bases.advance("Bert", 5)
        self.assertEquals(self.bases.fate_for(berts_fate_id_2),5)


    def test_fates_3(self):
        self.bases.advance("Bert", 4)
        berts_fate_id_1 = self.bases.player_fate_id("Bert")
        self.assertEquals(self.bases.fate_for(berts_fate_id_1),4)
