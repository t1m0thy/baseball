import uuid

class Bases:
    """ maintain a record of offensive player locations around the bases for game of baseball

    attributes:
    player_locations is a dictionary of player names and their current base location

    """

    def __init__(self):
        self.clear()

    def runner_names(self):
        """return tuple of names of players on (first, second, third)"""
        return (self.on_base(1),
                self.on_base(2),
                self.on_base(3),
                )

    def is_valid(self):
        """
        verify that no two players are on the same base

        """
        flipped_dict = dict((value, key) for key, value in self.player_locations.iteritems())
        return len(flipped_dict) == len(self.player_locations)

    def on_base(self, base_num):
        for player, base in self.player_locations.items():
            if base == base_num:
                return player
        return None

    def runner_count(self):
        return len(self.player_locations)

    def remove(self, player_name):
        del(self.player_locations[player_name])
        del(self.fates_id_lookup[player_name])

    def clear(self):
        self.player_locations = {}
        self.fates_dict = {}
        self.fates_id_lookup = {None: 0}
        #self.fates_bases = [0,0,0,0]

    def advance(self, player_name, base):
        """ advance player to new base_num.  return the advance string ie. "1-2" """
        if base not in [1, 2, 3, 4, 5, 6]:
            raise ValueError("base_num advances must be specified with an integer: 1,2,3,4,5,6")
        if base > 4:
            base_num = 4
        else:
            base_num = base

        if player_name in self.player_locations:
            assert (base_num > self.player_locations[player_name])
            startbase = self.player_locations[player_name]
            if base_num == 4:
                # left bases with score
                del(self.player_locations[player_name])
        else:
            startbase = 'B'
            self.new_fate(player_name)

        self.fates_dict[self.fates_id_lookup[player_name]] = base

        if base_num == 4:
            endbase = 'H'
        else:
            self.player_locations[player_name] = base_num
            endbase = str(base_num)

        return "{}-{}".format(startbase, endbase)

    def get_runner_base(self, player_name):
        return self.runner_names().index(player_name) + 1

    def replace_runner(self, new_player, replacing_player, base=None):
        if base is None:
            base =  self.get_runner_base(replacing_player)
        if self.on_base(base) != replacing_player:
            raise StandardError("{} is not on base {} for {} to replace".format(replacing_player, base, new_player))
        replacing_runner_fate_id = self.player_fate_id(replacing_player)
        self.remove(replacing_player)
        self.fates_id_lookup[new_player] = replacing_runner_fate_id
        self.player_locations[new_player] = base
        return base

    def code(self):
        """
        return the base code according to this lookup:

        BASE CODE LOOKUP
        CD:  short:  long:
        0    ___    Empty
        1    1__    1B only
        2    _2_    2B only
        3    12_    1B & 2B
        4    __3    3B only
        5    1_3    1B & 3B
        6    _23    2B & 3B
        7    123    Loaded
        """
        # 1 if on base, 0 if not
        base_state =  [str(int(self.on_base(i) != None)) for i in (3,2,1)]
        return int(''.join(base_state), 2)

    def new_fate(self, player_name):
        new_uuid = uuid.uuid4()
        self.fates_dict[new_uuid] = 0
        self.fates_id_lookup[player_name] = new_uuid

    def player_fate_id(self, player_name):
        return self.fates_id_lookup[player_name]

    def runners_fate_ids(self):
        return [self.player_fate_id(name) for name in self.runner_names()]

    def fate_for(self, fate_id):
        return self.fates_dict[fate_id]

