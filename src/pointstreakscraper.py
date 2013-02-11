import logging
import lxml
from bs4 import BeautifulSoup
import os
import json

from models.playerinfo import PlayerInfo

from scrapetools import GameScraper, HalfInning, RawEvent
from scrapetools import get_cached_url
from lineup import Lineup, Player, PlayerList, LineupError
import constants

BASE_DIR = os.path.dirname(__file__)
DEFAULT_CACHE_PATH = os.path.join(BASE_DIR, "../htmlcache/")
GAME_CACHE_PATH = "games/game_%s.html"
GAME_XML_CACHE_PATH = "games/game_%s.xml"
GAME_XML_SEQ_CACHE_PATH = "games/game_%s_seq_%s.xml"
PLAYER_CACHE_PATH = "players/player_%s.html"


logger = logging.getLogger("pointstreak scraper")

PS_GAME_XML = "http://v0.pointstreak.com/baseball/flashapp/getlivegamedata.php?gameid=%s"
PS_GAME_SEQUENCE_XML = "http://v0.pointstreak.com/baseball/flashapp/getlivegamedata.php?gameid=%s&sequenceid=%s"
PS_GAME_HTML = "http://www.pointstreak.com/baseball/boxscore.html?gameid=%s"
PS_2012_CCL_URL = "http://www.pointstreak.com/baseball/schedule.html?leagueid=166&seasonid=12252"
PS_2012_CCL_STATS = "http://www.pointstreak.com/baseball/stats.html?leagueid=166&seasonid=18269&view=batting"

PS_PLAYER_URL = "http://www.pointstreak.com/baseball/player.html?playerid=%s"

DIV_ID_AWAY_BOX = "psbb_box_score_away"
DIV_ID_HOME_BOX = "psbb_box_score_home"
DIV_ID_BATTING_STATS = "psbb_battingStats"
DIV_ID_PITCHING_STATS = "psbb_pitchingStats"
DIV_ID_PLAYBYPLAY = "psbb_playbyplay"
DIV_ID_GAME_SUMMARY = "psbb_game_summary"

MAX_EVENTS_COUNT = 40


class ScrapeError(Exception):
    pass


def make_xml_url(gameid):
    """ the xml url used for parsing game.  useful for reviewing site source """
    return PS_GAME_XML % str(gameid)


def make_xml_seq_url(gameid, seq):
    """ the xml sequence url used for parsing game.  useful for reviewing site source """
    return PS_GAME_SEQUENCE_XML % (str(gameid), str(seq))


def make_html_url(gameid):
    """ the html url used for parsing game.  useful for reviewing site source """
    return PS_GAME_HTML % str(gameid)
    
#===============================================================================
# GameID Scraping
#===============================================================================

PS_JSON_URL = "http://www.pointstreak.com/baseball/ajax/schedule_ajax.php?action=showalldates&s={}"
    
def scrape_pointstreak_gameids(html):
    playoff_soup = BeautifulSoup(html)
    links = playoff_soup.find_all("a")
    scores = [l for l in links if l.text == "final"]
    gameids = [s.attrs["href"].split('=')[1] for s in scores]
    return gameids

def scrape_season_gameids(seasonid, cache_path=None):
    if cache_path is None:
        cache_path = DEFAULT_CACHE_PATH
    LISTINGS_CACHE_PATH = os.path.join(cache_path, "listings","list_{}.json".format(seasonid))
    season = get_cached_url(PS_JSON_URL.format(seasonid), LISTINGS_CACHE_PATH)
    html = json.loads(season)["html"]
    ids = scrape_pointstreak_gameids(html)
    return ids

class PointStreakScraper(GameScraper):
    def __init__(self, gameid, cache_path=None):
        self.gameid = str(gameid)
        if cache_path is not None:
            self._cache_path = cache_path            
        else:
            self._cache_path = DEFAULT_CACHE_PATH
        self._home_html_player_list = PlayerList()
        self._away_html_player_list = PlayerList()

        xml = self._get_pointstreak_xml()
        self.root = lxml.etree.fromstring(xml)
        self.game_info = dict(self.root.find(".//{*}BaseballGame").items())
        self._build_html_player_tables()

    def home_team(self):
        """ return name of home team """
        return self.game_info["HomeTeam"]

    def away_team(self):
        """ return name of away team """
        return self.game_info["VisitingTeam"]

    def halfs(self):
        """ iterator that returns HalfInning Objects through the game """
        halfs = [e for e in self.root.find(".//{*}PlayByPlay").getchildren()]
        for half in halfs:  #what a mouthful!
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
        away_roster.update_players(self._make_players(is_home=False, player_dict_list=away_offense + away_replaced + away_pitchers))
        home_roster.update_players(self._make_players(is_home=True, player_dict_list=home_offense + home_replaced + home_pitchers))
        
        self._complete_player_profile(False, away_roster)
        self._complete_player_profile(True, home_roster)
        return away_roster, home_roster

    def scrape_lineup_from_seq_xml(self, seq):
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

        away_offense_player_list = self._make_players(is_home=False, player_dict_list=away_offense)
        away_defense_player_list = self._make_players(is_home=False, player_dict_list=away_defense)

        if away_pitchers:
            starting_pitcher = self._make_pitcher(is_home=False, player_dict=away_pitchers[0])
            if starting_pitcher is not None:
                try:
                    away_defense_player_list.find_player_by_name(starting_pitcher.name)
                    away_defense_player_list.update_player(starting_pitcher)
                except KeyError:
                    away_defense_player_list.insert(0, starting_pitcher)

        
        home_offense_player_list = self._make_players(is_home=False, player_dict_list=home_offense)
        home_defense_player_list = self._make_players(is_home=False, player_dict_list=home_defense)

        if home_pitchers:
            starting_pitcher = self._make_pitcher(is_home=True, player_dict=home_pitchers[0])
            if starting_pitcher is not None:
                try:
                    home_defense_player_list.find_player_by_name(starting_pitcher.name)
                    home_defense_player_list.update_player(starting_pitcher)
                except KeyError:
                    home_defense_player_list.insert(0, starting_pitcher)
        return away_offense_player_list + away_defense_player_list, home_offense_player_list + home_defense_player_list
            
    def starting_lineups(self):
        complete = False
        seq = 1
        away_lineup = Lineup()
        home_lineup = Lineup()

        while not complete:
            try:
                away_player_list, home_player_list = self.scrape_lineup_from_seq_xml(seq)
        
                for p in away_player_list:
                    if p.position not in away_lineup.position_dict() and p.name is not None:
                        away_lineup.update_player(p)
                for p in home_player_list:
                    if p.position not in home_lineup.position_dict() and p.name is not None:
                        home_lineup.update_player(p)
                
                try:
                    complete = home_lineup.is_complete(raise_reason=False)
                except LineupError, e:
                    logging.error(str(e) + "\nHome \n" + str(home_lineup))

                try:
                    complete &= away_lineup.is_complete(raise_reason=False)
                except LineupError, e:
                    logging.error(str(e) + "\nAway \n" + str(away_lineup))

            except lxml.etree.XMLSyntaxError:
                logger.error("Error parsing lineup from game %s seq %s" % (self.gameid, seq))
            seq += 1
            if seq > MAX_EVENTS_COUNT:
                # check each lineup for completeness, raising the reason for incomplete
                home_lineup.is_complete(raise_reason=True)
                away_lineup.is_complete(raise_reason=True)

        self._complete_player_profile(False, away_lineup)
        self._complete_player_profile(True, home_lineup)
        return away_lineup, home_lineup

    def get_player_info(self, player_id):
        html = self._player_page_from_id(player_id)
        soup = BeautifulSoup(html)
        divs = soup.find_all("div", {"id": "psbb_player_info"})
        if divs:
            player_info = divs[0]
        else:
            raise ScrapeError("Not finding any divs in html page for player url {}".format(self._player_url_from_id(player_id)))
        #photo_url = player_info.find_all("img")[0].attrs.get("src")
        rows = [c for c in player_info.table.table.table.find_all("td")]
        info_dict = dict([r.text.strip().split(":") for r in rows])
        pinfo = PlayerInfo()
        bats_throws = info_dict.get("Bats/Throws").split("/")
        if len(bats_throws) > 0:
            pinfo.BAT_HAND = bats_throws[0].strip()
        if len(bats_throws) > 1:
            pinfo.THROW_HAND = bats_throws[1].strip()
        pinfo.BIRTHDAY = info_dict.get("Birthdate")
        pinfo.COLLEGE_YEAR = info_dict.get("Class")
        pinfo.COLLEGE_NAME = info_dict.get("College")
        pinfo.DRAFT_STATUS = info_dict.get("Draft Status")
        pinfo.HEIGHT = info_dict.get("Height")
        pinfo.HOMETOWN = info_dict.get("Hometown")
        pinfo.POSITIONS = info_dict.get("Position")
        pinfo.WEIGHT = info_dict.get("Weight")
        return pinfo

    def _get_point_streak_url(self):
        return make_html_url(self.gameid)

    def _get_pointstreak_game_html(self, force_reload=False):
        url = self._get_point_streak_url()
        cache_filename = os.path.join(self._cache_path, GAME_CACHE_PATH % ("PS" + self.gameid))
        return get_cached_url(url, cache_filename, force_reload)

    def _get_pointstreak_xml(self, seq=None, force_reload=False):
        if seq is None:
            url = make_xml_url(self.gameid)
            cache_filename = os.path.join(self._cache_path, GAME_XML_CACHE_PATH % ("PS" + self.gameid))
        else:
            url = make_xml_seq_url(self.gameid, seq)
            cache_filename = os.path.join(self._cache_path, GAME_XML_SEQ_CACHE_PATH % (("PS" + self.gameid), seq))
        return get_cached_url(url, cache_filename, force_reload)

    def _make_pitcher(self, is_home, player_dict):
        new_player = Player(player_dict.get("Name"),
                                  player_dict.get("Number"),
                                  player_dict.get("Order"),
                                  constants.P,
                                  player_dict.get("Hand"),
                                  iddict={"pointstreak": None})
        if new_player.name is not None:
            new_player.name = new_player.name.replace("&apos;","'").replace("_apos;","'")
            return new_player
        else:
            return None
    def _make_players(self, is_home, player_dict_list):
        out = PlayerList()
        for player_dict in player_dict_list:
            try:
                new_player = Player(player_dict.get("Name"),
                                      player_dict.get("Number"),
                                      player_dict.get("Order"),
                                      player_dict.get("Position"),
                                      player_dict.get("Hand"),
                                      iddict={"pointstreak": None})
                if new_player.name is not None:
                    new_player.name = new_player.name.replace("&apos;","'").replace("_apos;","'")
                    out.add_player(new_player)
            except (AttributeError, KeyError):
                logger.error("making Player from dict = %s" % player_dict)
                raise
        return out

    def _div_id_dict(self, element):
        return dict((d.attrs["id"], d) for d in element.findAll("div") if d.has_attr("id"))

    def get_player_id(self, is_home, player):
        if is_home:
            search_list = self._home_html_player_list
        else:
            search_list = self._away_html_player_list
        try:
            bestmatch = player.find_closest_name(search_list)
            return bestmatch.iddict.get("pointstreak")
        except:
            logger.error("Failed to find match for:\n{} \nin list:\n{}".format(player, search_list))
            raise
        
    def _update_html_player_table(self, is_home, table):
        if is_home:
            current_list = self._home_html_player_list
        else:
            current_list = self._away_html_player_list
        for t in table.find_all("tr"):
            if t.a is not None:
                #[u'2', u'Campbell, D', u'SS', u'4', u'0', u'0', u'0', u'0', u'1', u'.302']
                table_values = [td.text for td in t.find_all("td")]
                player_num = table_values[0]
                player_name = table_values[1]
                player_id = t.a.attrs.get("href").split('=')[1]
                player = Player(player_name, player_num, iddict={"pointstreak": player_id})
                current_list.update_player(player)
                
    def _build_html_player_tables(self):
        html = self._get_pointstreak_game_html()
        soup = BeautifulSoup(html)
        divs = self._div_id_dict(soup)

        batting_stats_div = divs[DIV_ID_BATTING_STATS]
        self._batting_stats_tables = batting_stats_div.find_all("table")

        self._update_html_player_table(is_home=False, table=self._batting_stats_tables[0])
        self._update_html_player_table(is_home=True, table=self._batting_stats_tables[1])

        pitching_stats_div = divs[DIV_ID_PITCHING_STATS]
        self._pitching_stats_tables = pitching_stats_div.find_all("table")

        self._update_html_player_table(is_home=False, table=self._pitching_stats_tables[0])
        self._update_html_player_table(is_home=True, table=self._pitching_stats_tables[1])

    def _player_url_from_id(self, player_id):
        return PS_PLAYER_URL % player_id

    def _player_page_from_id(self, player_id):
        """ return point streak html from a player id """
        player_cache_path = os.path.join(self._cache_path, PLAYER_CACHE_PATH % ("PS" + str(player_id)))
        return get_cached_url(self._player_url_from_id(player_id), player_cache_path)
        
    def _complete_player_profile(self, is_home, player_list):
        for player in player_list:
            try:
                player_id = self.get_player_id(is_home, player)
                player_info = self.get_player_info(player_id)
                #TODO: I don't don't if 'P' in POSITIONS is safe or correct - TDH 2-2013
                player.throw_hand = player_info.THROW_HAND
                player.bat_hand = player_info.BAT_HAND
            except:
                player.bat_hand = '?'
                player.throw_hand = '?'
                logger.exception("Unable to find more info on {}".format(player.name))
                

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
        event_type, text, batter, number, sub_type = tag, element.text, element.attrib.get("Name"), element.attrib.get("Number"), element.attrib.get("Type")
        try:
            assert(event_type in ["Atbat", "Substitution"])
        except AssertionError:
            logger.exception("Found event tag %s" % event_type)
        self._type = event_type
        self._batter_name = batter
        self._batter_number = number
        # If this is a sub, add the Type to the beginning of the string: ie.  "Offensive Substitution"
        if sub_type != None:
            text = sub_type + '. ' + text
        self._text = text

    def is_sub(self):
        return self._type == "Substitution"

    def batter(self):
        if self.is_sub():
            return StandardError("No batter for substitution event")
        else:
            return self._batter_name.replace("&apos;","'").replace("_apos;","'")
    def batter_number(self):
        if self.is_sub():
            return StandardError("No batter for substitution event")
        else:
            return self._batter_number

    def text(self):
        return self._text.replace("&apos;","'").replace("_apos;","'")

    def title(self):
        if self.is_sub():
            return self._type
        else:
            return "{} #{} {}".format(self._type, self._batter_number, self._batter_name)
            



