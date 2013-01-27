from constants import POSITIONS, DH, P, POSITION_LOOKUP

class LineupError(Exception):
    pass

class Player:
    def __init__(self, name, number, order, position, hand, iddict={}):
        self.name = name
        self.number = number
        try:
            self.order = int(order)
        except TypeError:
            self.order = None
        self.position = self._verified_position(position)
        self.hand = hand
        self.iddict = iddict
        self.atbats = 0
        #TODO: add throwing hand vs. batting hand
        #TODO: add switch_hitter flag

    def _verified_position(self, position):
        if position is not None:
            return POSITION_LOOKUP[position.lower()]
        else:
            return None

    def __eq__(self, other):
        return self.name == other.name and self.number == other.number

    def __str__(self):
        return "%2s %3s %s %3s %2s" % (self.order, self.number, self.name.ljust(18), self.position, self.hand)

    def set_position(self, position):
        self.position = self._verified_position(position)


class PlayerList(list):
    """
    maintain one team's line up or 9 or 10 players
    """
    def __init__(self):
        list.__init__(self)

    def add_players(self, player_list):
        """
        add any player objects from list
        default, only add if players have numbers
        """
        for p in player_list:
            self.add_player(p)

    def add_player(self, player):
        """add_player if not already in lineup"""
        if player not in self:
            self.append(player)
        else:
            raise LineupError("%s already in lineup" % player.name)

    def update_player(self, player):
        """add_player.
        if already in lineup, replace old player
        """
        my_player_numbers = [p.number for p in self]
        if player.number is None:
            raise KeyError("All Players must have numbers")
        if player.number not in my_player_numbers:
            self.append(player)
        else:
            replace_index = my_player_numbers.index(player.number)
            self[replace_index] = player
#        else:
#            raise LineupError("%s already in lineup" % name)

    def find_player_by_name(self, name):
        for p in self:
            if p.name == name:
                return p
        raise KeyError("No player found with name %s" % name)

    def set_player_position(self, name, position):
        self.find_player_by_name(name).set_position(position)

    def __str__(self):
        tmp = self

        def ordercmp(x, y):
            return cmp(x.order, y.order)
        tmp.sort(cmp=ordercmp)
        out = "\n".join([str(p) for p in tmp])
        return out


class Lineup(PlayerList):
    def move_player(self, name, new_position):
        """ move player from old position to new."""
        self.find_player_by_name(name).position = new_position

    def remove_player(self, name):
        """remove player with name from lineup

        returns removed player
        """
        p = self.find_player_by_name(name)
        self.remove(p)
        return p

    def is_complete(self, raise_reason=False):
        """
        check that current lineup is valid
        all field positions and all batting order slots filled and not duplicated
        """
        try:
            self.find_player_by_position(DH)
            if len(self) > 10:
                if raise_reason:
                    raise LineupError("Over 10 players in the lineup")
                return False
        except KeyError:
            # no DH, so there should be a pitcher in the order
            try:
                if self.find_player_by_position(P).order == None:
                    if raise_reason:
                        raise LineupError("No DH in lineup and pitcher not in order")
                    return False
            except KeyError:
                if raise_reason:
                    raise LineupError("No DH in and no pitcher")
                return False

            if len(self) > 9:
                if raise_reason:
                    raise LineupError("Over 9 in lineup with no DH")
                return False

                #raise LineupError("Over 9 players in the lineup")
        try:
            for i in range(1, 10):
                self.find_player_by_order(i)
        except KeyError:
            if raise_reason:
                raise LineupError("Missing order number %s" % i)
            return False

        try:
            for p in POSITIONS:
                self.find_player_by_position(p)
        except KeyError:
            if raise_reason:
                raise LineupError("Missing position %s" % p)
            return False

        return True

    def find_player_by_position(self, position):
        """
        retrieve player
        position - one of the position codes "P", "C", "1B", etc
                    or the position number (1: pitcher, 2: catcher, etc)
        """
        position = POSITION_LOOKUP[position.lower()]
        for p in self:
            if p.position == position:
                return p
        raise KeyError("No player found at position %s" % position)

    def find_player_by_order(self, order):
        """
        retrieve player with their batting order
        """
        for p in self:
            if p.order == order:
                return p
        raise KeyError("No player found at order number %s" % order)

    def position_dict(self):
        return dict([(p.position, p.name) for p in self])

    def has_position(self, position):
        try:
            self.find_player_by_position(position)
            return True
        except KeyError:
            return False
