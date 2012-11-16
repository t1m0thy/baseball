import pyparsing as pp
import lxml

from gamewrapper import GameWrapper
from scrapetools import get_game_html
from lineup import Lineup
import constants

import logging
logger = logging.getLogger("pointstreakparser")
from constants import GAME_CACHE_PATH, GAME_XML_CACHE_PATH, GAME_XML_SEQ_CACHE_PATH, POSITIONS

PS_GAME_XML = "http://v0.pointstreak.com/baseball/flashapp/getlivegamedata.php?gameid=%s"
PS_GAME_SEQUENCE_XML = "http://v0.pointstreak.com/baseball/flashapp/getlivegamedata.php?gameid=%s&sequenceid=%s"
PS_GAME_HTML = "http://www.pointstreak.com/baseball/boxscore.html?gameid=%s"
PS_2012_CCL_URL = "http://www.pointstreak.com/baseball/schedule.html?leagueid=166&seasonid=12252"
PS_2012_CCL_PLAYOFF_URL = "http://www.pointstreak.com/baseball/schedule.html?leagueid=166&seasonid=18269"
PS_2012_CCL_STATS = "http://www.pointstreak.com/baseball/stats.html?leagueid=166&seasonid=18269&view=batting"

PS_PLAYER_URL = "http://www.pointstreak.com/baseball/player.html?playerid="

DIV_ID_AWAY_BOX = "psbb_box_score_away"
DIV_ID_HOME_BOX = "psbb_box_score_home"
DIV_ID_BATTING_STATS = "psbb_battingStats"
DIV_ID_PITCHING_STATS = "psbb_pitchingStats"
DIV_ID_PLAYBYPLAY = "psbb_playbyplay"
DIV_ID_GAME_SUMMARY = "psbb_game_summary"


def get_point_streak_url(gameid):
    return PS_GAME_HTML % gameid

def get_pointstreak_game(gameid, force_reload=False):
    url = get_point_streak_url(gameid)
    cache_filename = GAME_CACHE_PATH%gameid
    return get_game_html(url, cache_filename, force_reload)
    
def get_pointstreak_xml(gameid, seq=None, force_reload=False):
    if seq is None:
        url = PS_GAME_XML % gameid 
        cache_filename = GAME_XML_CACHE_PATH % gameid
    else:
        url = PS_GAME_SEQUENCE_XML % (gameid, seq)
        cache_filename = GAME_XML_SEQ_CACHE_PATH % (gameid, seq)
    return get_game_html(url, cache_filename, force_reload)
        
                
def add_pitcher(lineup, player):
    lineup.add_player(player.get("Name"), 
                  player.get("Number"), 
                  player.get("Order"), 
                  constants.P, 
                  player.get("Hand"),
                  iddict={"pointstreak":player.get("PlayerId")})

def add_positions(lineup, playerlist):
    for player in playerlist:
        try:
            lineup.add_player(player.get("Name"), 
                              player.get("Number"), 
                              player.get("Order"), 
                              player.get("Position"), 
                              player.get("Hand"),
                              iddict={"pointstreak":player.get("PlayerId")})
        except AttributeError:
            logger.exception("from player = %s" % player)
            
def scrape_pointstreak_xml_lineups(gameid):
    complete = False
    seq = 0
    while not complete:
        try:
            xml = get_pointstreak_xml(gameid, seq)    
            root = lxml.etree.fromstring(xml)
            away_offense = [dict(e.items()) for e in root.find(".//{*}VisitingTeam").find(".//{*}Offense").getchildren()]
            home_offense = [dict(e.items()) for e in root.find(".//{*}HomeTeam").find(".//{*}Offense").getchildren()]
            away_defense = [dict(e.items()) for e in root.find(".//{*}VisitingTeam").find(".//{*}Defense").getchildren()]
            home_defense = [dict(e.items()) for e in root.find(".//{*}HomeTeam").find(".//{*}Defense").getchildren()]
            away_pitchers = [dict(e.items()) for e in root.find(".//{*}VisitingTeam").find(".//{*}Pitchers").getchildren()]
            home_pitchers = [dict(e.items()) for e in root.find(".//{*}HomeTeam").find(".//{*}Pitchers").getchildren()]
    
            away_lineup = Lineup()     
            add_positions(away_lineup, away_offense)
            add_positions(away_lineup, away_defense)
            if len(away_pitchers) > 0:
                add_pitcher(away_lineup, away_pitchers[0])
            
            home_lineup = Lineup()
            add_positions(home_lineup, home_offense)
            add_positions(home_lineup, home_defense)
            if len(home_pitchers) > 0:
                add_pitcher(home_lineup, home_pitchers[0])

            try:
                complete = home_lineup.is_complete(True)
            except StandardError, e:
                print [p.order for p in home_lineup.players]
                logging.error(str(e) + "\nHome \n" + str(home_lineup))
                print home_lineup.find_player_by_order(1)

            try:
                complete &= away_lineup.is_complete(True)            
            except StandardError, e:
                logging.error(str(e) + "\nAway \n" + str(away_lineup))
    
        except lxml.etree.XMLSyntaxError:
            print "Error parsing game %s seq %s" % (gameid, seq)
            if seq > 300:
                raise
        seq += 1
    return away_lineup, home_lineup
    
class PointStreakParser:
    def __init__(self, game=None):
        self.gamewrap = GameWrapper(game)
        self.setup_parser()
        
    def set_game(self, game):
        self.gamewrap.set_game(game)
        
    def setup_parser(self):
        #===========================================================================
        # General Parser Items
        #===========================================================================
    
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
        
        out_description = (left_paren + pp.OneOrMore(possibles | pp.Word(pp.alphanums+':')) + right_paren).addParseAction(self.gamewrap.describe_out) 
        
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
        fielder_sub = player.setResultsName("new player") + ((pp.Keyword("subs for") + player_no_num + pp.Keyword("at")) | (pp.Keyword("moves to")|pp.Keyword("subs at"))) + position.setResultsName("position") + period
        fielder_sub.setParseAction(self.gamewrap.fielder_sub)
        offensive_sub = player.setResultsName("new player") + pp.Keyword("subs for") + player_no_num.setResultsName("replacing") + period
        offensive_sub.setParseAction(self.gamewrap.offensive_sub)
        runner_sub = player.setResultsName("new player") + pp.Keyword("runs for") + player_no_num.setResultsName("replacing") + pp.Keyword("at") + pp.Word(pp.alphanums).setResultsName("base") + pp.Word(pp.alphanums)  + period
        runner_sub.setParseAction(self.gamewrap.offensive_sub)
        
        #===========================================================================
        # Summary 
        #===========================================================================
        self.event_parser = pp.delimitedList(fielder_sub | offensive_sub | runner_sub | pitches | advances | putout | scores)  + pp.StringEnd()
        
    def parsePlay(self, text):
        self.event_parser.parseString(text)
        return self.gamewrap._game