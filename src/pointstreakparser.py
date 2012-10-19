import pyparsing as pp
from gamewrapper import GameWrapper
        
    
class PointStreakParser:
    def __init__(self, game=None):
        self.set_game(game)
        self.setup_parser()
        
    def set_game(self, game):
        self.gamewrap = GameWrapper(game)
        
    def setup_parser(self):
        #===========================================================================
        # General Parser Items
        #===========================================================================
    
        comma = pp.Literal(',').suppress()
        dash = pp.Literal('-').suppress()
        left_paren = pp.Literal('(').suppress()
        right_paren = pp.Literal(')').suppress()
        period = pp.Literal('.').suppress()
    
        paranthetical = left_paren + pp.OneOrMore(pp.Word(pp.alphanums+"'")) + right_paren  # single quote in words for "fielder's choice"
        player_no_num = pp.Word(pp.alphas+'.').setResultsName("firstname") + pp.Optional(pp.Keyword('St.')) + pp.Word(pp.alphas).setResultsName("lastname")
        player = (pp.Word(pp.nums).setResultsName("playernum") + player_no_num).setResultsName("player")
        
        #===========================================================================
        # PITCHING    
        #===========================================================================
        pickoff_attempt = (pp.Keyword("Pickoff attempt at") + pp.OneOrMore(pp.Word(pp.alphanums)) + paranthetical).setParseAction(self.gamewrap.pickoff)
        swinging = pp.Keyword("Swinging Strike", caseless=True).setParseAction(self.gamewrap.swinging_strike)
        called = pp.Keyword("Called Strike", caseless=True).setParseAction(self.gamewrap.called_strike)
        ball = pp.Keyword("Ball", caseless=True).setParseAction(self.gamewrap.ball)
        foul = pp.Keyword("Foul", caseless=True).setParseAction(self.gamewrap.foul)
    
        #===============================================================================
        #  Outs
        #===============================================================================
        unassisted_out = pp.Word(pp.nums) + (pp.Literal('U') | pp.Literal('u'))
        thrown_out = pp.delimitedList(pp.Word(pp.nums), "-")
        double_play = pp.Keyword("DP", caseless=True).setResultsName("doubleplay")
        triple_play = pp.Keyword("TP", caseless=True).setResultsName("tripleplay")
        picked_off = pp.Keyword("PO").setResultsName("pickoff")
        sacrifice_hit =  pp.Keyword("SH").setResultsName("sacrifice hit")
        dropped_third_strike = (pp.Keyword("KS")).setResultsName("dropped third")
        caught_stealing = (pp.Keyword("CS")).setResultsName("caught stealing")
        strike_out = pp.Keyword("Strike Out", caseless = True) + pp.Optional(pp.Keyword("swinging"))
        fly_out = pp.Keyword("Fly out to", caseless = True) + pp.OneOrMore(pp.Word(pp.alphas)).setResultsName("field position") 
        
        possibles = double_play | triple_play | picked_off | sacrifice_hit | dropped_third_strike | caught_stealing | thrown_out | unassisted_out | strike_out | fly_out
        
        out_description = (left_paren + pp.OneOrMore(possibles | pp.Word(pp.alphanums)) + right_paren).addParseAction(self.gamewrap.describe_out) 
        
        putout = (player + pp.Keyword("putout", caseless=True) + pp.Optional(out_description)).setParseAction(self.gamewrap.out) + pp.Keyword("for out number") + pp.Word(pp.nums)
        
        #===============================================================================
        # Base Running
        #===============================================================================
    
        advances = (player + pp.Keyword("advances to", caseless=True) + pp.OneOrMore(pp.Word(pp.alphanums)).setResultsName("base") + paranthetical.copy().setResultsName("info")).setParseAction(self.gamewrap.advance)
            
        #===========================================================================
        # Scoring
        #===========================================================================
        earned = pp.Keyword("Earned", caseless = True) + paranthetical.copy().setResultsName("play")
        unearned = pp.Keyword("Unearned", caseless = True) + paranthetical.copy().setResultsName("player_num")
        scores = (player + pp.Keyword("scores", caseless=True) + (unearned | earned)).setParseAction(self.gamewrap.score)
    
        #===========================================================================
        # SUBS
        #===========================================================================
        position = pp.OneOrMore(pp.Word(pp.alphanums))
        fielder_sub = player.setResultsName("new player") + (pp.Keyword("moves to")|pp.Keyword("subs at")) + position.setResultsName("position") + period
        fielder_sub.setParseAction(self.gamewrap.fielder_sub)
        offensive_sub = player.setResultsName("new player") + pp.Keyword("subs for") + player_no_num.setResultsName("replacing") + period
        offensive_sub.setParseAction(self.gamewrap.offensive_sub)
        runner_sub = player.setResultsName("new player") + pp.Keyword("runs for") + player_no_num.setResultsName("replacing") + pp.Keyword("at") + pp.Word(pp.alphanums).setResultsName("base") + pp.Word(pp.alphanums)  + period
        runner_sub.setParseAction(self.gamewrap.offensive_sub)
        
        #===========================================================================
        # Summary 
        #===========================================================================
        self.event_parser = pp.delimitedList(fielder_sub | offensive_sub | runner_sub | swinging | called | ball | foul | pickoff_attempt | advances | putout | scores)  + pp.StringEnd()
        
    def parsePlay(self, text):
        self.event_parser.parseString(text)