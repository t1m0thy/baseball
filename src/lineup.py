from constants import POSITIONS, DH, P

class Player:
    def __init__(self, name, number, order, position, hand, iddict={}):
        self.name = name
        self.number = number
        try:
            self.order = int(order)
        except TypeError:
            self.order = None
        self.position = position
        self.hand = hand
        self.iddict = iddict

    def __eq__(self, other):
        return self.name == other.name and self.number == other.number
    
    def __str__(self):
        return "%2s %3s %s %3s %2s" % (self.order, self.number, self.name.ljust(18), self.position, self.hand)

class PlayerError(BaseException): pass
    
class Lineup(object):
    """
    maintain one team's line up or 9 or 10 players
    """
    def __init__(self):
        self.players = []
        
    def add_player(self, name, number, order, position, hand, iddict={}):
        p = Player(name, number, order, position, hand, iddict={})
        if p not in self.players:
            self.players.append(p)
            
    def move_player(self, name, new_position):
        """
        move player from old position to new.
        """
        self.find_player_by_name(name).position  = new_position
    
    def remove_player(self, name):
        """
        remove player from lineup
        """        
        success = False
        for p in self.players:
            if p.name == name:
                del(p)
                success = True
        return success

    
    def is_complete(self, raise_reason = False):
        """
        check that current lineup is valid
        all field positions and all batting order slots filled and not duplicated
        """
        try:
            self.find_player_by_position(DH)
            if len(self.players) > 10:
                if raise_reason:
                    raise StandardError("Over 10 players in the lineup")
                return False
        except KeyError:
            # no DH, so there shoudl be a pitcher in the order
            try:
                if self.find_player_by_position(P).order == None:
                    if raise_reason:
                        raise StandardError("No DH in lineup and pitcher not in order")
                    return False
            except KeyError:
                if raise_reason:
                    raise StandardError("No DH in and no pitcher")
                return False
                
            if len(self.players) > 9:
                if raise_reason:
                    raise StandardError("Over 9 in lineup with no DH")
                return False
                
                #raise StandardError("Over 9 players in the lineup")            
        try:
            for i in range(1,10):
                self.find_player_by_order(i)
        except KeyError:
            if raise_reason:
                raise StandardError("Missing order number %s" % i)
            return False
            
        try:
            for p in POSITIONS:
                self.find_player_by_position(p)
        except KeyError:
            if raise_reason:
                raise StandardError("Missing position %s" % p)
            return False
            
        return True
                
        
    def find_player_by_position(self, position):
        """
        retrieve player
        position - one of the position codes "P", "C", "1B", etc
                    or the position number (1: pitcher, 2: catcher, etc)
        """
        for p in self.players:
            if p.position == position:
                return p
        raise KeyError("No player found at position %s" % position)

    def find_player_by_name(self, name):
        for p in self.players:
            if p.name == name:
                return p
        raise KeyError("No player found with name %s" % name)

    
    def find_player_by_order(self, order):
        """
        retrieve player with their batting order
        """
        for p in self.players:
            if p.order == order:
                return p
        raise KeyError("No player found at order number %s" % order)

    def position_dict(self):
        return dict([(p.position, p.name) for p in self.players])
    
    def has_position(self, position):
        try:
            self.find_player_by_position(position)
            return True
        except KeyError:
            return False
        
    def __str__(self):
        tmp = self.players
        def ordercmp(x,y):
            return cmp(x.order, y.order)
        tmp.sort(cmp=ordercmp)
        out = "\n".join([str(p) for p in tmp])
        return out