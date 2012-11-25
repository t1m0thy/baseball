import logging
import lxml


from scrapetools import GameScraper, HalfInning, RawEvent
from scrapetools import get_cached_url
from lineup import Lineup, Player, PlayerList
import constants

CACHE_PATH = "../htmlcache/"
GAME_CACHE_PATH = CACHE_PATH + "games/game_%s.html"
GAME_XML_CACHE_PATH = CACHE_PATH + "games/game_%s.xml"
GAME_XML_SEQ_CACHE_PATH = CACHE_PATH + "games/game_%s_seq_%s.xml"

PLAYER_CACHE_PATH = CACHE_PATH + "players/player_%s.html"
LISTINGS_CACHE_PATH = CACHE_PATH + "listings/list_%s.html" 


logger = logging.getLogger("pointstreak scraper")

PS_GAME_XML = "http://v0.pointstreak.com/baseball/flashapp/getlivegamedata.php?gameid=%s"
PS_GAME_SEQUENCE_XML = "http://v0.pointstreak.com/baseball/flashapp/getlivegamedata.php?gameid=%s&sequenceid=%s"
PS_GAME_HTML = "http://www.pointstreak.com/baseball/boxscore.html?gameid=%s"
PS_2012_CCL_URL = "http://www.pointstreak.com/baseball/schedule.html?leagueid=166&seasonid=12252"
PS_2012_CCL_PLAYOFF_URL = "http://www.pointstreak.com/baseball/schedule.html?leagueid=166&seasonid=18269"
PS_2012_CCL_STATS = "http://www.pointstreak.com/baseball/stats.html?leagueid=166&seasonid=18269&view=batting"

PS_PLAYER_URL = "http://www.pointstreak.com/baseball/player.html?playerid=%s"

DIV_ID_AWAY_BOX = "psbb_box_score_away"
DIV_ID_HOME_BOX = "psbb_box_score_home"
DIV_ID_BATTING_STATS = "psbb_battingStats"
DIV_ID_PITCHING_STATS = "psbb_pitchingStats"
DIV_ID_PLAYBYPLAY = "psbb_playbyplay"
DIV_ID_GAME_SUMMARY = "psbb_game_summary"

MAX_EVENTS_COUNT = 30


class PointStreakScraper(GameScraper):
    def __init__(self, gameid):
        self.gameid = gameid
        
    def _get_point_streak_url(self):
        return PS_GAME_HTML % self.gameid
    
    def _get_pointstreak_game_html(self, force_reload=False):
        url = self._get_point_streak_url()
        cache_filename = GAME_CACHE_PATH % ("PS" + self.gameid)
        return get_cached_url(url, cache_filename, force_reload)
        
    def _get_pointstreak_xml(self, seq=None, force_reload=False):
        if seq is None:
            url = PS_GAME_XML % self.gameid 
            cache_filename = GAME_XML_CACHE_PATH % ("PS" + self.gameid)
        else:
            url = PS_GAME_SEQUENCE_XML % (self.gameid, seq)
            cache_filename = GAME_XML_SEQ_CACHE_PATH % (("PS" + self.gameid), seq)
        return get_cached_url(url, cache_filename, force_reload)            
                    
    def _add_pitcher(self, lineup, player_dict):
        lineup.add_player(Player(player_dict.get("Name"), 
                                  player_dict.get("Number"), 
                                  player_dict.get("Order"), 
                                  constants.P, 
                                  player_dict.get("Hand"),
                                  iddict={"pointstreak":player_dict.get("PlayerId")}))
    
    def _add_positions(self, lineup, playerlist):
        for player_dict in playerlist:
            try:
                lineup.add_player(Player(player_dict.get("Name"), 
                                          player_dict.get("Number"), 
                                          player_dict.get("Order"), 
                                          player_dict.get("Position"), 
                                          player_dict.get("Hand"),
                                          iddict={"pointstreak":player_dict.get("PlayerId")}))
            except (AttributeError, KeyError):
                logger.error("making Player from dict = %s" % player_dict)
                raise
    def starting_lineups(self):
        complete = False
        seq = 0
        while not complete:
            try:
                xml = self._get_pointstreak_xml(seq)
                root = lxml.etree.fromstring(xml)
                away = root.find(".//{*}VisitingTeam")
                away_offense = [dict(e.items()) for e in away.find(".//{*}Offense").getchildren()]
                away_defense = [dict(e.items()) for e in away.find(".//{*}Defense").getchildren()]
                away_pitchers = [dict(e.items()) for e in away.find(".//{*}Pitchers").getchildren()]
                home = root.find(".//{*}HomeTeam")
                home_offense = [dict(e.items()) for e in home.find(".//{*}Offense").getchildren()]
                home_defense = [dict(e.items()) for e in home.find(".//{*}Defense").getchildren()]
                home_pitchers = [dict(e.items()) for e in home.find(".//{*}Pitchers").getchildren()]
        
                away_lineup = Lineup()     
                self._add_positions(away_lineup, away_offense)
                self._add_positions(away_lineup, away_defense)
                if len(away_pitchers) > 0:
                    self._add_pitcher(away_lineup, away_pitchers[0])
                
                home_lineup = Lineup()
                self._add_positions(home_lineup, home_offense)
                self._add_positions(home_lineup, home_defense)
                if len(home_pitchers) > 0:
                    self._add_pitcher(home_lineup, home_pitchers[0])
    
                try:
                    complete = home_lineup.is_complete(raise_reason = False)
                except StandardError, e:
                    logging.error(str(e) + "\nHome \n" + str(home_lineup))
    
                try:
                    complete &= away_lineup.is_complete(raise_reason = False)            
                except StandardError, e:
                    logging.error(str(e) + "\nAway \n" + str(away_lineup))
        
            except lxml.etree.XMLSyntaxError:
                logger.error("Error parsing lineup from game %s seq %s" % (self.gameid, seq))
            seq += 1
            if seq > MAX_EVENTS_COUNT:
                # check each lineup for completeness, raising the reason for incomplete
                home_lineup.is_complete(raise_reason = True)
                away_lineup.is_complete(raise_reason = True)
            
        return away_lineup, home_lineup
      
class PSPHalfInningXML(HalfInning):
    def __init__(self, etree):
        self._etree = etree
        
    def raw_events(self):
        for e in self._etree.getchildren():
            tag = e.tag.split("}")[-1]
            if tag != "Summary":
                yield PSPRawEventXML(e)

class PSPRawEventXML(RawEvent):
    def __init__(self, element):
        tag = element.tag.split("}")[-1]
        event_type, text, batter, sub_type = tag, element.text, element.attrib.get("Name"), element.attrib.get("Type") 
        try:
            assert(event_type in ["Atbat", "Substitution"])
        except AssertionError, e:
            print event_type
            logger.exception("Found event tag %s" % event_type)
        self._type = event_type
        self._batter = batter
        # If this is a sub, add the Type to the beginning of the string: ie.  "Offensive Substitution"
        if sub_type != None:
            text = sub_type+'. '+text
        self._text = text
    
    def is_sub(self):
        return self._type == "Substitution"

    def batter(self):
        if self.is_sub():
            return StandardError("No batter for substitution event")
        else:
            return self._batter

    def text(self):
        return self._text 
    
    def title(self):
        if self.is_sub():
            return self._type
        else:
            return self._type + " " + self._batter

class PointStreakXMLScraper(PointStreakScraper):
    def __init__(self, gameid):
        PointStreakScraper.__init__(self, gameid)
        xml = self._get_pointstreak_xml()
        self.root = lxml.etree.fromstring(xml)
        self.game_info = dict(self.root.find(".//{*}BaseballGame").items())

    def home_team(self):
        """ return name of home team """
        return self.game_info["HomeTeam"]

    def away_team(self):
        """ return name of away team """
        return self.game_info["VisitingTeam"]

    def review_url(self):
        """ the url used for parsing game.  useful for reviewing site source """
        return PS_GAME_XML % self.gameid 

    def halfs(self):
        """ iterator that returns HalfInning Objects through the game """
        halfs = [e for e in self.root.find(".//{*}PlayByPlay").getchildren()]
        for half in halfs: #what a mouthful!
            yield PSPHalfInningXML(half)
            
    def game_rosters(self):
        """ return full list of all players in the game """
        away = self.root.find(".//{*}VisitingTeam")
        away_offense = [dict(e.items()) for e in away.find(".//{*}Offense").getchildren()]
        away_replaced = [dict(e.items()) for e in away.find(".//{*}ReplacedOffense").getchildren()]
        away_pitchers = [dict(e.items() + [("Position", "P")]) for e in away.find(".//{*}Pitchers").getchildren()]

        home = self.root.find(".//{*}HomeTeam")
        home_offense = [dict(e.items()) for e in home.find(".//{*}Offense").getchildren()]
        home_replaced = [dict(e.items()) for e in home.find(".//{*}ReplacedOffense").getchildren()]
        home_pitchers = [dict(e.items() + [("Position", "P")]) for e in home.find(".//{*}Pitchers").getchildren()]
                    
        away_roster = PlayerList()
        home_roster = PlayerList()
        self._add_positions(away_roster, away_offense + away_replaced + away_pitchers)
        self._add_positions(home_roster, home_offense + home_replaced + home_pitchers)

        return away_roster, home_roster

    def _player_page_from_id(self, player_id):
        """ return point streak html from a player id """
        return get_cached_url(PS_PLAYER_URL % player_id, PLAYER_CACHE_PATH % ("PS" + str(player_id)))
        