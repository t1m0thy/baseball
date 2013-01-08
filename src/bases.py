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
        
    def clear(self):
        self.player_locations = {}
        
    def advance(self, player_name, base):
        """ advance player to new base.  return the advance string ie. "1-2" """  
        if base not in [1,2,3,4]:
            raise ValueError("base advances must be specified with an integer: 1,2,3,4")
        if player_name in self.player_locations:
            assert (base > self.player_locations[player_name])
            startbase = self.player_locations[player_name]
            if base == 4:
                # left bases with score
                self.remove(player_name)
        else:    
            startbase = 'B'
            
        if base == 4:
            endbase = 'H'
        else:
            self.player_locations[player_name] = base
            endbase = str(base)
        
        return "{}-{}".format(startbase, endbase)
        
    def replace_runner(self, new_player, replacing_player, base):
        assert(replacing_player == self.on_base(base))
        self.remove(replacing_player)
        self.advance(new_player, base)
        
