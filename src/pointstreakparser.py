import pyparsing as pp

from gamewrapper import GameWrapper


import logging
logger = logging.getLogger("pointstreak parser")
            

class PointStreakParser:
    """
    
    """
    def __init__(self, game=None):
        self.gamewrap = GameWrapper(game)
        self.setup_parser()
        
    def set_game(self, game):
        self.gamewrap.set_game(game)
        
    def setup_parser(self):
        #===========================================================================
        # General Parser Items
        #===========================================================================
    
        #TODO: use constants to all arguments passed to setResultsName
        #comma = pp.Literal(',').suppress()
        dash = pp.Literal('-').suppress()
        left_paren = pp.Literal('(').suppress()
        right_paren = pp.Literal(')').suppress()
        period = pp.Literal('.').suppress()
    
        paranthetical = left_paren + pp.OneOrMore(pp.Word(pp.alphanums+"'")) + right_paren  # single quote in words for "fielder's choice"
        player_no_num = pp.Word(pp.alphas+'.').setResultsName("firstname") + pp.Optional(pp.Keyword('St.')) + pp.Word(pp.alphas).setResultsName("lastname")
        player = (pp.Word(pp.nums).setResultsName("playernum") + player_no_num).setResultsName("player")
        
        
        error = pp.Literal("E")+pp.Word(pp.nums)
        #===========================================================================
        # PITCHING    
        #===========================================================================
        pickoff_attempt = (pp.Keyword("Pickoff attempt at") + pp.OneOrMore(pp.Word(pp.alphanums)) + paranthetical).setParseAction(self.gamewrap.pickoff)
        swinging = pp.Keyword("Swinging Strike", caseless=True).setParseAction(self.gamewrap.swinging_strike)
        called = pp.Keyword("Called Strike", caseless=True).setParseAction(self.gamewrap.called_strike)
        ball = pp.Keyword("Ball", caseless=True).setParseAction(self.gamewrap.ball)
        foul = pp.Keyword("Foul", caseless=True).setParseAction(self.gamewrap.foul)
        dropped_foul = pp.Keyword("Dropped Foul", caseless=True).setParseAction(self.gamewrap.foul) + pp.Optional(dash + error) 
    
        pitches = dropped_foul | swinging | called | ball | foul | pickoff_attempt
        #===============================================================================
        #  Outs
        #===============================================================================
        unassisted_out = pp.Word(pp.nums) + pp.CaselessLiteral('U')
        thrown_out = pp.delimitedList(pp.Word(pp.nums), "-")
        double_play = pp.CaselessLiteral("DP").setResultsName("doubleplay")
        triple_play = pp.CaselessLiteral("TP").setResultsName("tripleplay")
        picked_off = pp.CaselessLiteral("PO").setResultsName("pickoff")
        sacrifice_hit =  pp.CaselessLiteral("SH").setResultsName("sacrifice hit")
        dropped_third_strike = (pp.CaselessLiteral("KS")).setResultsName("dropped third")
        caught_stealing = (pp.CaselessLiteral("CS")).setResultsName("caught stealing")
        strike_out = pp.Keyword("Strike Out", caseless = True) + pp.Optional(pp.Keyword("swinging"))
        fly_out = pp.Keyword("Fly out to", caseless = True) + pp.OneOrMore(pp.Word(pp.alphas)).setResultsName("field position") 
        
        possibles = double_play | triple_play | picked_off | sacrifice_hit | dropped_third_strike | caught_stealing | thrown_out | unassisted_out | strike_out | fly_out
        
        out_description = (left_paren + pp.OneOrMore(possibles | pp.Word(pp.alphanums+':')) + right_paren).setResultsName("description") 
        
        putout = (player + pp.Keyword("putout", caseless=True) + pp.Optional(out_description)).setParseAction(self.gamewrap.out) + pp.Keyword("for out number") + pp.Word(pp.nums)
        
        #===============================================================================
        # Base Running
        #===============================================================================
        base = pp.OneOrMore(pp.Word(pp.alphanums)).setResultsName("base")
        advances = (player + pp.Keyword("advances to", caseless=True) + base + paranthetical.copy().setResultsName("info")).setParseAction(self.gamewrap.advance)
            
        #===========================================================================
        # Scoring
        #===========================================================================
        end_span =  pp.Optional(pp.Literal('</span>')).suppress()
        earned_span = pp.Optional(pp.Literal('<span class="earned">')).suppress()
        unearned_span = pp.Optional(pp.Literal('<span class="unearned">')).suppress()
        score_span = pp.Optional(pp.Literal('<span class="score">')).suppress()
        earned = earned_span + pp.Keyword("Earned", caseless = True) + end_span + paranthetical.setResultsName("play")
        unearned = unearned_span + pp.Keyword("Unearned", caseless = True) + end_span + paranthetical.setResultsName("player_num")
        score_word = score_span + pp.Keyword("scores", caseless=True) + end_span
        scores = (player + score_word + (unearned | earned)).setParseAction(self.gamewrap.score)
    
        #===========================================================================
        # SUBS
        #===========================================================================
        replacing = player_no_num.setResultsName("replacing")
        new_player = player.setResultsName("new player")
        position = pp.OneOrMore(pp.Word(pp.alphanums))
        defensive_sub = pp.Keyword("Defensive Substitution.") + new_player + ((pp.Keyword("subs for") + replacing + pp.Keyword("at")) | (pp.Keyword("moves to")|pp.Keyword("subs at"))) + position.setResultsName("position") + period
        defensive_sub.setParseAction(self.gamewrap.defensive_sub)
        dh_sub = pp.Keyword("Defensive Substitution.") + new_player + pp.Keyword("subs for") + replacing + period
        dh_sub.setParseAction(self.gamewrap.defensive_sub)

        pitching_sub = pp.Keyword("Pitching Substitution.") + new_player + pp.Keyword("subs for") + replacing + period
        pitching_sub.setParseAction(self.gamewrap.defensive_sub)

        offensive_sub = pp.Keyword("Offensive Substitution.") + new_player + pp.Keyword("subs for") + replacing + period
        offensive_sub.setParseAction(self.gamewrap.offensive_sub)
        runner_sub = pp.Keyword("Offensive Substitution.") + new_player + pp.Keyword("runs for") + replacing + pp.Keyword("at") + pp.Word(pp.alphanums).setResultsName("base") + pp.Word(pp.alphanums)  + period
        runner_sub.setParseAction(self.gamewrap.offensive_sub)
        
        subs = defensive_sub | dh_sub | pitching_sub | offensive_sub | runner_sub
        #===========================================================================
        # Summary 
        #===========================================================================
        self.event_parser = pp.delimitedList(subs | pitches | advances | putout | scores)  + pp.StringEnd()
        
    def parse_event(self, text):
        self.last_event_text = text
        self.event_parser.parseString(text)
        return self.gamewrap._game
    

