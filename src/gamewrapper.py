import constants

class GameWrapper:
    """
    GameWrap.  This class is a wrapper around the gamestate class.
    
    It allows gamestate instances to be swapped out without needing to re-hook the calls
    setup in a parser.  
    """
    
    def __init__(self, game=None):
        self.set_game(game)
    
    def set_game(self, game):
        self._game = game
        
    def pickoff(self, *args):
        self._game.add_pickoff(*args)
    
    def swinging_strike(self, *args):
        self._game.add_swinging_strike(*args)
    
    def called_strike(self, *args):
        self._game.add_called_strike(*args)
    
    def ball(self, *args):
        self._game.add_ball(*args)
    
    def foul(self, *args):
        self._game.add_foul(*args)
    
    def out(self, *args):
        self.parse_out(*args)
    
    def advance(self, *args):
        self.parse_advance(*args)
    
    def score(self, *args):
        self.parse_score(*args)
    
    def defensive_sub(self, *args):
        self.parse_defensive_sub(*args)
    
    def offensive_sub(self, *args):
        self.parse_offensive_sub(*args)
        
        
    def parse_offensive_sub(self, text, location, tokens):
        new_player_name = ' '.join(tokens[constants.PARSING.NEW_PLAYER][1:])
        replacing_name = ' '.join(tokens.get(constants.PARSING.REPLACING, []))
        self._game.offensive_sub(new_player_name, replacing_name)        
        
    def parse_defensive_sub(self, text, location, tokens):
        new_player_name = ' '.join(tokens[constants.PARSING.NEW_PLAYER][1:])
        replacing_name = ' '.join(tokens.get(constants.PARSING.REPLACING, []))
        position = ' '.join(tokens.get(constants.PARSING.POSITION, []))
        self._game.defensive_sub(new_player_name, replacing_name, position)      
        
    def parse_advance(self, text, location, tokens):
        tdict = tokens.asDict()
        player_name = ' '.join(tdict[constants.PARSING.PLAYER][1:])
        base = tdict["base"][0]
        self._game.add_advance(player_name, base)
        
    def parse_out(self, text, location, tokens):
        tdict = tokens.asDict()    
        player_name = ' '.join(tdict[constants.PARSING.PLAYER][1:])
        play = tdict[constants.PARSING.DESCRIPTION]
        self._game.add_out(player_name, play)
        
    def parse_score(self, text, location, tokens):
        tdict = tokens.asDict()
        player_name = ' '.join(tdict[constants.PARSING.PLAYER][1:])
        self._game.add_score(player_name)
       
