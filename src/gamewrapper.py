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
    
    def describe_out(self, *args):
        self._game.add_out_description(*args)
    
    def out(self, *args):
        self._game.add_out(*args)
    
    def advance(self, *args):
        self._game.add_advance(*args)
    
    def score(self, *args):
        self._game.add_score(*args)
    
    def fielder_sub(self, *args):
        self._game.fielder_substitution(*args)
    
    def offensive_sub(self, *args):
        self._game.offensive_substitution(*args)
