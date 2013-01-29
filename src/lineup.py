from constants import POSITIONS, DH, P, POSITION_LOOKUP


class LineupError(Exception):
    pass


class Player:
    def __init__(self, name, number=None, order=None, position=None, hand=None, iddict={}):
        """
        setup Player object
        
        names presented in "last, first" (as given with comma) order will be switched (Smith, Joe => Joe Smith)
        positions are verified and looked up to become the character version ie. 'LF' or '1B'
        """
        
        try:
            name = name.strip()
            if ',' in name:
                last, first = name.split(',', 1)
                name = first.strip() + ' ' + last.strip()
        except AttributeError:
            pass
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
        return len(self.diff(other)) == 0 

    def __str__(self):
        return "%2s %3s %s %3s %2s" % (self.order, self.number, str(self.name).ljust(18), self.position, self.hand)

    def set_position(self, position):
        self.position = self._verified_position(position)

    def merge(self, other):
        """ Any attributes of player that are not None will overwrite the value of this current player.
        iddict is updates with data from player as well """
        for attr in ["name", "number", "order", "position", "hand"]:
            if other.__dict__[attr] is not None:
                self.__dict__[attr] = other.__dict__[attr]
        self.iddict.update(other.iddict)

    def diff(self, other):
        """return dictionary of any values that differ with other player.
        key is the key, and then the value tuple contains local and other values
        """
        diffs = {}
        for k, v in vars(self).items():
            if vars(other)[k] != v:
                diffs[k] = (v, vars(other)[k])
        return diffs
    
    def calc_match_score(self, other):
        points = 0
        if self.name == other.name:
            points += 4
        elif self.name is not None:
            myfirst, mylast = self.name.split(' ', 1)
            otherfirst, otherlast = other.name.split(' ', 1)
            if mylast == otherlast:
                points += 2
            try:
                if myfirst[0] == otherfirst[0]:
                    points += 1
            except IndexError:
                print "{} vs {}".format(myfirst, other.name)
                pass
        if self.number == other.number:
            points += 1
        if self.position == other.position:
            points += 1
        return points
            
    def find_closest(self, player_list):
        match_scores = [self.calc_match_score(other) for other in player_list]
        best_score = max(match_scores)
        winner_count = match_scores.count(best_score)
        if winner_count == 1:
            return player_list[match_scores.index(best_score)]
        else:
            raise ValueError("No single good match.  Tie between {} entries.  player {}".format(winner_count, self))

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

    def update_players(self, player_list):
        """
        add any player objects from list
        default, only add if players have numbers
        """
        for p in player_list:
            self.update_player(p)
#        
#    def __add__(self, player_list):
#        new_list = PlayerList()
#        new_list.add_players(self)
#        new_list.add_players(player_list)
#        return new_list
     
    def add_player(self, player):
        """add_player if not already in lineup"""
        if player not in self:
            self.append(player)
        else:
            raise LineupError("{} already in lineup:\n {}".format(player.name, str(self)))

    def update_player(self, player):
        """add_player.
        if already in lineup, replace old player
        """
        my_player_names = [p.name for p in self]
        if player.name is None:
            raise KeyError("All Players must have names")
        if player.name not in my_player_names:
            self.append(player)
        else:
            replace_index = my_player_names.index(player.name)
            current_player = self[replace_index]
            current_player.merge(player)

    def find_player_by_name(self, name):
        for p in self:
            if p.name == name:
                return p
        raise KeyError("No player found with name %s" % name)

    def find_player_by_number(self, number):
        for p in self:
            if str(p.number) == str(number):
                return p
        raise KeyError("No player found with number %s" % number)

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
