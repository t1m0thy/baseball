from constants import POSITIONS, DH, P, POSITION_LOOKUP, LEFT, RIGHT, UNKNOWN, SWITCH
import difflib
import itertools
from models import playerinfo
from collections import OrderedDict

class LineupError(Exception):
    pass


class Name(str):
    """ will test quality with lower case, and stripped"""
    def __new__(self, name):
        try:
            name = name.strip()
            name = name.replace("&apos;", "'").replace("_apos;", "'")
            if ',' in name:
                last, first = name.split(',', 1)
                name = first.strip() + ' ' + last.strip()
            name = " ".join([word[0].upper() + word[1:] for word in name.split(" ") if word != ''])
        except AttributeError:
            pass
        self._id = None
        return str.__new__(self, name)

    def id(self):
        if self._id is not None:
            return self._id
        else:
            try:
                first, last = self.split(" ", 1)
                return last.replace(" ", "")[:4].lower() + first[0].lower()
            except ValueError:
                return self.replace(" ", "")[:5].lower()

    def set_id(self, _id):
        self._id = _id

    def __eq__(self, other):
        if self.lower() == Name(str(other)).lower():
            return True
        if self.id() is not None:
            if self.id() == str(other):
                return True
            elif hasattr(other, "id") and self.id() == other.id():
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def first(self):
        splitname = self.split(' ', 1)
        if len(splitname) == 2:
            return splitname[0]
        else:
            return ""

    def last(self):
        splitname = self.split(' ', 1)
        if len(splitname) == 2:
            return splitname[1]
        else:
            return splitname[0]


class Player:
    def __init__(self, name, number=None, order=None, position=None, bat_hand='?', throw_hand='?', iddict={}, team_id=None, starter=None):
        """
        setup Player object

        names presented in "last, first" (as given with comma) order will be switched (Smith, Joe => Joe Smith)
        positions are verified and looked up to become the character version ie. 'LF' or '1B'
        """
        self._needs_to_sub = False
        self._pinch_hitter = False
        self._replacing_field_position = None

        self.name = name
        if name is not None:
            self.name = Name(self.name)

        try:
            self.number = int(number)
        except:
            self.number = None

        try:
            self.order = int(order)
        except TypeError:
            self.order = None
        self.position = self._verified_position(position)
        if self.position is not None:
            self.all_positions = [self.position]
        else:
            self.all_positions = []

        if bat_hand is None:
            bat_hand = UNKNOWN
        if bat_hand not in [LEFT,
                            RIGHT,
                            SWITCH,
                            UNKNOWN]:
            raise StandardError("Unknown Bat hand type: {}".format(bat_hand))
        self.bat_hand = bat_hand

        if throw_hand is None:
            throw_hand = UNKNOWN
        if throw_hand not in [LEFT,
                              RIGHT,
                              UNKNOWN]:
            raise StandardError("Unknown throw hand type: {}".format(bat_hand))

        self.throw_hand = throw_hand

        self.iddict = iddict
        self.team_id = team_id

        self.plate_appearances = 0
        self.bat_stats = dict(AB=0, H=0, R=0, RBI=0, BB=0, SO=0, AVG=0)
        self.pitch_stats = dict(IP=0, H=0, R=0, ER=0, BB=0, SO=0, ERA=0)
        self.verify_bat_stats = {}
        self.verify_pitch_stats = {}
        self.starter = starter
        if self.starter:
            self.starting_position = position
            self.starting_order = order
        else:
            self.starting_position = None
            self.starting_order = None

        #TODO: add throwing hand vs. batting hand
        #TODO: add switch_hitter flag

    def as_odict(self):
        out = OrderedDict()
        for attr in ["name",
                     "iddict",
                     "number",
                     "order",
                     "position",
                     "all_positions",
                     "bat_hand",
                     "throw_hand",
                     "birthday",
                     "college_year",
                     "college_name",
                     "draft_status",
                     "height",
                     "weight",
                     "team_id",
                     "starter",
                     "starting_position",
                     "starting_order"]:
            out[attr] = getattr(self, attr)
        out.update(vars(self))
        return out

    def set_name(self, name):
        self.name = Name(name)

    def to_model(self, update_model=None):
        if update_model is None:
            out = playerinfo.PlayerInfo()
        else:
            out = update_model
        out.FIRST_NAME = self.name.first()
        out.LAST_NAME = self.name.last()
        out.BAT_HAND = self.bat_hand
        out.THROW_HAND = self.throw_hand
        out.BIRTHDAY = self.birthday
        out.COLLEGE_NAME = self.college_name
        out.COLLEGE_YEAR = self.college_year
        out.DRAFT_STATUS = self.draft_status
        out.HEIGHT = self.height
        out.HOMETOWN = self.hometown
        psid = self.iddict.get("pointstreak", -1)
        if psid is not None:
            out.ID_POINTSTREAK = int(psid)
        out.POSITIONS = ','.join(self.all_positions)
        out.WEIGHT = self.weight
        out.SBS_ID = self.name.id()
        out.TEAM_ID = self.team_id
        return out

    def _verified_position(self, position):
        if position is not None:
            return POSITION_LOOKUP[position.lower()]
        else:
            return None

    def __eq__(self, other):
        return len(self.diff(other)) == 0

    def __str__(self):
        return "%2s %3s %s %3s %2s (%s)" % (self.order, self.number, str(self.name).ljust(18), self.position, self.bat_hand, self.all_positions)

    def set_position(self, position):
        self.position = self._verified_position(position)
        if self.position is not None and self.position not in self.all_positions:
            self.all_positions.append(self.position)

    def merge(self, other):
        """ Any attributes of player that are not None will overwrite the value of this current player.
        iddict is updates with data from player as well """
        # only adopt the name if it's longer and more informative (this avoid single first initial overwriting full)
        if other.name is not None and len(other.name) > len(self.name):
            self.name = Name(other.name)

        #TODO: make these special attributes special with decorators or something...
        for attr in ["number",
                     "order",
                     "position",
                     "bat_hand",
                     "throw_hand",
                     "birthday",
                     "college_year",
                     "college_name",
                     "draft_status",
                     "height",
                     "weight",
                     "team_id",
                     "starter",
                     "starting_position",
                     "starting_order"]:
            if other.__dict__.get(attr) is not None:
                self.__dict__[attr] = other.__dict__[attr]
        for p in other.all_positions:
            if p is not None and p not in self.all_positions:
                self.all_positions.append(p)
        self.iddict.update(other.iddict)
        self.verify_pitch_stats.update(other.verify_pitch_stats)
        self.verify_bat_stats.update(other.verify_bat_stats)
        self.pitch_stats.update(other.pitch_stats)
        self.bat_stats.update(other.bat_stats)

    def diff(self, other):
        """return dictionary of any values that differ with other player.
        key is the key, and then the value tuple contains local and other values
        """
        diffs = {}
        for k, v in vars(self).items():
            if vars(other)[k] != v:
                diffs[k] = (v, vars(other)[k])
        return diffs

#    def calc_match_score(self, other):
#        points = 0
#        if self.name == other.name:
#            points += 4
#        elif self.name is not None:
#            names = self.name.split(' ', 1)
#            if len(names) == 2:
#                myfirst, mylast = names
#            else:
#                mylast = names
#            names = other.name.split(' ', 1)
#            if len(names) == 2:
#                otherfirst, otherlast = names
#            else:
#                otherlast = names
#            if mylast.lower() == otherlast.lower():
#                points += 2
#                try:
#                    if myfirst[0].lower() == otherfirst[0].lower():
#                        points += 1
#                except IndexError:
#                    pass
#
#        if self.number == other.number:
#            points += 1
#        if self.position == other.position:
#            points += 1
#        return points

    def find_closest_name(self, player_list):
        other_names = [other.name.lower() for other in player_list]
        matches = difflib.get_close_matches(self.name.lower(), other_names, n=1, cutoff=0.6)
        winner_count = len(matches)
        if winner_count == 0:
            matches = difflib.get_close_matches(self.name.split()[-1].lower(), other_names, n=1, cutoff=0.6)
            winner_count = len(matches)

        if winner_count == 1:
            return player_list[other_names.index(matches[0])]
        else:
            raise ValueError("No single good match found in set of closest: {} for player {}".format(matches, self.name))

    def set_pending_sub(self, set_to=True):
        self._needs_to_sub = set_to

    def is_pending_sub(self):
        return self._needs_to_sub

    def set_pinch_hitter(self, set_to=True):
        self._pinch_hitter = set_to

    def is_pinch_hitter(self):
        return self._pinch_hitter

    def set_replacing_field_position(self, position):
        """
        when a player pinch hits, sometimes their fielding position isn't clarified,
        or it's clarified late in the next inning.  this is a marker for their likely field position if
        it's not specified
        """
        self._replacing_field_position = position

    def get_replacing_field_position(self):
        return self._replacing_field_position


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

    def max_order(self):
        orders = [p.order for p in self]
        return max(orders)


    def add_player(self, player):
        """add_player if not already in lineup"""
        if player not in self:
            self.append(player)
        else:
            raise LineupError("{} already in lineup:\n {}".format(player.name, str(self)))

    def update_player(self, player):
        """add_player.
        if already in lineup, replace old player
        return True if added, False if merged with old
        """
        my_player_names = [p.name for p in self]
        if player.name is None:
            raise StandardError("All Players must have names")
        if player.name not in my_player_names:
            self.append(player)
            return True
        else:
            merge_index = my_player_names.index(player.name)
            current_player = self[merge_index]
            if current_player.iddict != player.iddict:
                self.append(player)
                return True
            else:
                current_player.merge(player)
                return False

    def find_player_by_name(self, name):
        name = name.strip()
        for p in self:
            if p.name == name:
                return p
        # for p in self:
        #     if p.name.split(' ')[-1] == name.split(' ')[-1]:
        #         return p

        raise KeyError("No player found with name %s" % name)

    def find_player_by_number(self, number):
        for p in self:
            if int(p.number) == int(number):
                return p
        raise KeyError("No player found with number %s" % number)

    def find_player_by_position(self, position):
        for p in self:
            if p.position == position:
                return p
        raise KeyError("No player found with position %s" % position)

    def find_player_by_id(self, idkey, idval):
        """
        retrieve player by matches in the iddict
        """
        for p in self:
            if p.iddict.get(idkey) == idval:
                return p
        raise KeyError("No player found with id {} = {}".format(idkey, idval))

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
                if self.find_player_by_position(P).order is None:
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

    def missing_fielders(self):
        missing = []
        currently_filled = self.position_dict()
        for p in POSITIONS:
            if p not in currently_filled:
                missing.append(p)
        return missing

    def has_position(self, position):
        try:
            self.find_player_by_position(position)
            return True
        except KeyError:
            return False

    def update_position(self, player):
        """
        if no position yet, put player in their specified position, otherwise, replace player at that position
        """
        try:
            replace_player = self.find_player_by_position(player.position)
            self.remove(replace_player)
            if player.order is None:
                player.order = replace_player.order
            self.add_player(player)
        except KeyError:
            self.add_player(player)

    def update_order(self, player):
        """
        if no position yet, put player in their specified position, otherwise, replace player at that position
        """
        try:
            replace_player = self.find_player_by_order(player.order)
            self.remove(replace_player)
        except KeyError:
            pass
        self.add_player(player)


    def find_complete_positions(self):
        """
        return a list of all valid position layouts for a team
        """
        save_positions = [p.position for p in self]
        options = []
        try:
            team_positions = [p.all_positions for p in self]
            for test_positions in itertools.product(*team_positions):
                for player, position in zip(self, test_positions):
                    player.position = position
                if self.is_complete():
                    options.append(test_positions)
        finally:
            for player, position in zip(self, save_positions):
                player.position = position

        return options

