import logging
import lxml
from bs4 import BeautifulSoup
import os

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

MAX_EVENTS_COUNT = 30


class ScrapeError(Exception):
    pass


class PointStreakScraper(GameScraper):
    def __init__(self, gameid, cache_path=None):
        self.gameid = gameid
        if cache_path is not None:
            self._cache_path = cache_path            
        else:
            self._cache_path = DEFAULT_CACHE_PATH
        self._home_playerid_by_num = {}
        self._away_playerid_by_num = {}

        xml = self._get_pointstreak_xml()
        self.root = lxml.etree.fromstring(xml)
        self.game_info = dict(self.root.find(".//{*}BaseballGame").items())
        self._build_player_id_lookup_dict()

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
        
        self._update_handedness(False, away_roster)
        self._update_handedness(True, home_roster)
        return away_roster, home_roster

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
                away_lineup.update_players(self._make_players(is_home=False, player_dict_list=away_offense), ignore_numberless=True)
                away_lineup.update_players(self._make_players(is_home=False, player_dict_list=away_defense), ignore_numberless=True)

                if len(away_pitchers) > 0:
                    starting_pitcher = self._make_pitcher(is_home=False, player_dict=away_pitchers[0])
                    try:
                        away_lineup.add_player(starting_pitcher)
                    except LineupError:
                        pitcher = away_lineup.find_player_by_name(starting_pitcher.name)
                        pitcher.merge(starting_pitcher)

                home_lineup = Lineup()
                home_lineup.update_players(self._make_players(is_home=False, player_dict_list=home_offense), ignore_numberless=True)
                home_lineup.update_players(self._make_players(is_home=False, player_dict_list=home_defense), ignore_numberless=True)
                if len(home_pitchers) > 0:
                    starting_pitcher = self._make_pitcher(is_home=True, player_dict=home_pitchers[0])
                    try:
                        home_lineup.add_player(starting_pitcher)
                    except LineupError:
                        pitcher = home_lineup.find_player_by_name(starting_pitcher.name)
                        pitcher.merge(starting_pitcher)
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

        self._update_handedness(False, away_lineup)
        self._update_handedness(True, home_lineup)
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
        return PS_GAME_HTML % self.gameid

    def _get_pointstreak_game_html(self, force_reload=False):
        url = self._get_point_streak_url()
        cache_filename = os.path.join(self._cache_path, GAME_CACHE_PATH % ("PS" + self.gameid))
        return get_cached_url(url, cache_filename, force_reload)

    def _get_pointstreak_xml(self, seq=None, force_reload=False):
        if seq is None:
            url = PS_GAME_XML % self.gameid
            cache_filename = os.path.join(self._cache_path, GAME_XML_CACHE_PATH % ("PS" + self.gameid))
        else:
            url = PS_GAME_SEQUENCE_XML % (self.gameid, seq)
            cache_filename = os.path.join(self._cache_path, GAME_XML_SEQ_CACHE_PATH % (("PS" + self.gameid), seq))
        return get_cached_url(url, cache_filename, force_reload)

    def _make_pitcher(self, is_home, player_dict):
        return Player(player_dict.get("Name"),
                                  player_dict.get("Number"),
                                  player_dict.get("Order"),
                                  constants.P,
                                  player_dict.get("Hand"),
                                  iddict={"pointstreak": None})

    def _make_players(self, is_home, player_dict_list):
        out = []
        for player_dict in player_dict_list:
            try:
                new_player = Player(player_dict.get("Name"),
                                      player_dict.get("Number"),
                                      player_dict.get("Order"),
                                      player_dict.get("Position"),
                                      player_dict.get("Hand"),
                                      iddict={"pointstreak": None})
                out.append(new_player)
            except (AttributeError, KeyError):
                logger.error("making Player from dict = %s" % player_dict)
                raise
        return out

    def _div_id_dict(self, element):
        return dict((d.attrs["id"], d) for d in element.findAll("div") if d.has_attr("id"))

    def get_player_id_from_team_and_number(self, is_home, player_number):
        if is_home:
            return self._home_playerid_by_num[player_number]
        else:
            return self._away_playerid_by_num[player_number]

    def _update_player_id_lookup_with_table(self, is_home, table):
        for t in table.find_all("tr"):
            if t.a is not None:
                player_num = t.td.text 
                player_id = t.a.attrs.get("href").split('=')[1]
                if is_home:
                    self._home_playerid_by_num[player_num] = player_id
                else:
                    self._away_playerid_by_num[player_num] = player_id

    def _build_player_id_lookup_dict(self):
        html = self._get_pointstreak_game_html()
        soup = BeautifulSoup(html)
        self.divs = self._div_id_dict(soup)

        batting_stats_div = self.divs[DIV_ID_BATTING_STATS]
        batting_stats_tables = batting_stats_div.find_all("table")

        self._update_player_id_lookup_with_table(is_home=False, table=batting_stats_tables[0])
        self._update_player_id_lookup_with_table(is_home=True, table=batting_stats_tables[1])

        pitching_stats_div = self.divs[DIV_ID_PITCHING_STATS]
        pitching_stats_tables = pitching_stats_div.find_all("table")

        self._update_player_id_lookup_with_table(is_home=False, table=pitching_stats_tables[0])
        self._update_player_id_lookup_with_table(is_home=True, table=pitching_stats_tables[1])

    def _player_url_from_id(self, player_id):
        return PS_PLAYER_URL % player_id

    def _player_page_from_id(self, player_id):
        """ return point streak html from a player id """
        player_cache_path = os.path.join(self._cache_path, PLAYER_CACHE_PATH % ("PS" + str(player_id)))
        return get_cached_url(self._player_url_from_id(player_id), player_cache_path)
        
    def _update_handedness(self, is_home, player_list):
        for player in player_list:
            player_id = self.get_player_id_from_team_and_number(is_home, player.number)
            player_info = self.get_player_info(player_id)
            player.hand = player_info.THROW_HAND


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
        except AssertionError:
            print event_type
            logger.exception("Found event tag %s" % event_type)
        self._type = event_type
        self._batter = batter
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
            return self._batter

    def text(self):
        return self._text

    def title(self):
        if self.is_sub():
            return self._type
        else:
            return self._type + " " + self._batter



