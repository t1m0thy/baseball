import logging
import lxml
from bs4 import BeautifulSoup, Tag
import os
import json
import string

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
    LISTINGS_CACHE_PATH = os.path.join(cache_path, "listings", "list_{}.json".format(seasonid))
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

        html = self._get_pointstreak_game_html()
        self.soup = BeautifulSoup(html)

        self._home_html_player_list = PlayerList()
        self._away_html_player_list = PlayerList()

        xml = self._get_pointstreak_xml()
        self.root = lxml.etree.fromstring(xml)
        self.game_info = dict(self.root.find(".//{*}BaseballGame").items())

        navdiv = self.soup.find_all("div", {"id": "psbb_nav_league"})
        league_id, season_id = navdiv[0].ul.li.a.attrs.get("href").split("?")[1].split("&")

        league_id = league_id.split("=")[1]
        season_id = season_id.split("=")[1]

        self.game_info["league_id"] = league_id
        self.game_info["season_id"] = season_id

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
        for half in halfs:  # what a mouthful!
            yield PSPHalfInningXML(half)


    def starting_lineups(self):
        complete = False
        away_lineup = Lineup()
        home_lineup = Lineup()

        away_roster = PlayerList()
        home_roster = PlayerList()

        away_player_list = [p for p in self._away_html_player_list]
        home_player_list = [p for p in self._home_html_player_list]

        for player_list, roster, starting_lineup in ((away_player_list, away_roster, away_lineup),
                                                     (home_player_list, home_roster, home_lineup)):
            for p in player_list:
                if p.starter:
                    starting_lineup.update_player(p)
                roster.update_player(p)

        for lineup, which_lineup in [(home_lineup, "Home"), (away_lineup, "Away")]:
            try:
                if not lineup.is_complete(raise_reason=False):
                    options = lineup.find_complete_positions()
                    if len(options) == 1:
                        for player, position in zip(lineup, options[0]):
                            if player.position != position:
                                d = {"name": player.name,
                                     "to_p": position,
                                     "from_p": player.position}
                                logger.warning("Automatically Moving {name} to position {to_p} from position {from_p}".format(**d))
                                player.position = position
                    else:
                        s = "\n".join([p.name + " " + str(p.all_positions) for p in lineup])
                        raise StandardError("Can not determine complete fielding lineup from \n" + s)
            except LineupError, e:
                logging.error(str(e) + "\n" + which_lineup + "\n" + str(lineup))

        self._complete_player_profile(False, away_roster)
        self._complete_player_profile(True, home_roster)
        return away_lineup, home_lineup, away_roster, home_roster

    def get_player_info(self, player_id):
        html = self._player_page_from_id(player_id)
        soup = BeautifulSoup(html)
        full_name = soup.find("title").text.split("-", 1)[0]
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
        return full_name, pinfo

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

    def _div_id_dict(self, element):
        return dict((d.attrs["id"], d) for d in element.findAll("div") if d.has_attr("id"))

    def get_player_id_and_stats(self, is_home, player):
        if is_home:
            search_list = self._home_html_player_list
        else:
            search_list = self._away_html_player_list
        try:
            bestmatch = player.find_closest_name(search_list)
            return bestmatch.iddict.get("pointstreak"), bestmatch.verify_bat_stats, bestmatch.verify_pitch_stats
        except:
            logger.error("Failed to find match for:\n{} \nin list:\n{}".format(player, search_list))
            raise

    def _update_html_player_table(self, is_home, batting, table):
        """
        helper method to build player lists parsed from the html pages.
        """
        starting_pitcher = True
        order = 0
        if is_home:
            current_list = self._home_html_player_list
        else:
            current_list = self._away_html_player_list
        for t in table.find_all("tr"):
            if t.a is not None:
                # number, name,           P      AB    R     H     RBI   BB    SO     AVG
                #[u'2', u'Campbell, D', u'SS', u'4', u'0', u'0', u'0', u'0', u'1', u'.302']
                table_values = [td.text for td in t.find_all("td")]
                player_num = table_values[0]
                player_name = table_values[1]
                player_id = t.a.attrs.get("href").split('=')[1]

                if batting:
                    starter = player_name[0] != u"\xa0"
                    if starter:
                        order += 1
                        use_order = order
                    else:
                        use_order = None
                    positions = [p for p in t.find_all("td")[2].childGenerator() if type(p) is not Tag]
                    player_position = positions[0]
                    player = Player(player_name,
                                    player_num,
                                    order=use_order,
                                    position=player_position,
                                    iddict={"pointstreak": player_id},
                                    starter=starter)  # starting means no indent in lineup
                    player.all_positions = positions
                    player.verify_bat_stats = dict(AB=int(table_values[3]),
                                                   R=int(table_values[4]),
                                                   H=int(table_values[5]),
                                                   RBI=int(table_values[6]),
                                                   BB=int(table_values[7]),
                                                   SO=int(table_values[8]),
                                                   AVG=float(table_values[9])
                                                   )
                else:
                    player = Player(player_name, player_num, position='P', iddict={"pointstreak": player_id})
                    player.verify_pitch_stats = dict(IP=float(table_values[2]),
                                                     H=int(table_values[3]),
                                                     R=int(table_values[4]),
                                                     ER=int(table_values[5]),
                                                     BB=int(table_values[6]),
                                                     SO=int(table_values[7]),
                                                     ERA=float(table_values[8])
                                                     )
                    if starting_pitcher:
                        player.starter = True
                        starting_pitcher = False

                current_list.update_player(player)

    def _build_html_player_tables(self):
        """
        parse the rosters from the main game html page
        """
        divs = self._div_id_dict(self.soup)

        # it's important to parse pitching first so that a players status
        # as a starting batter will over ride a non-starting pitching scenario.
        # sometimes a player will move into relief from another position and keep batting
        pitching_stats_div = divs[DIV_ID_PITCHING_STATS]
        self._pitching_stats_tables = pitching_stats_div.find_all("table")

        self._update_html_player_table(is_home=False, batting=False, table=self._pitching_stats_tables[0])
        self._update_html_player_table(is_home=True, batting=False, table=self._pitching_stats_tables[1])

        batting_stats_div = divs[DIV_ID_BATTING_STATS]
        self._batting_stats_tables = batting_stats_div.find_all("table")

        self._update_html_player_table(is_home=False, batting=True, table=self._batting_stats_tables[0])
        self._update_html_player_table(is_home=True, batting=True, table=self._batting_stats_tables[1])


    def _player_url_from_id(self, player_id):
        return PS_PLAYER_URL % player_id

    def _player_page_from_id(self, player_id):
        """ return point streak html from a player id """
        player_cache_path = os.path.join(self._cache_path, PLAYER_CACHE_PATH % ("PS" + str(player_id)))
        return get_cached_url(self._player_url_from_id(player_id), player_cache_path)

    def _complete_player_profile(self, is_home, player_list):
        for player in player_list:
            player_id = None
            try:
                player_id, verify_bat_stats, verify_pitch_stats = self.get_player_id_and_stats(is_home, player)
                player.verify_bat_stats.update(verify_bat_stats)
                player.verify_pitch_stats.update(verify_pitch_stats)
            except:
                logger.exception("unable to find id for player {}".format(player.name))

            try:
                full_name, player_info = self.get_player_info(player_id)
                player.set_name(full_name)
                player.iddict["pointstreak"] = player_id
            except:
                logger.exception("Unable to find player with id: {}".format(player_id))

            try:
                #TODO: I don't don't if 'P' in POSITIONS is safe or correct - TDH 2-2013
                player.throw_hand = player_info.THROW_HAND
                player.bat_hand = player_info.BAT_HAND
            except:
                player.bat_hand = '?'
                player.throw_hand = '?'
                logger.exception("Unable to find handedness info on {}".format(player.name))

            try:
                player.birthday = player_info.BIRTHDAY
                player.college_name = player_info.COLLEGE_NAME
                player.college_year = player_info.COLLEGE_YEAR
                player.draft_status = player_info.DRAFT_STATUS
                player.height = player_info.HEIGHT
                player.hometown = player_info.HOMETOWN
                player.positions = player_info.POSITIONS
                player.weight = player_info.WEIGHT
            except:
                logger.exception("Unable to find extra info on {}".format(player.name))


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
        if sub_type is not None:
            text = sub_type + '. ' + text
        self._text = text

    def is_sub(self):
        return self._type == "Substitution"

    def batter(self):
        if self.is_sub():
            return StandardError("No batter for substitution event")
        else:
            return self._batter_name.replace("&apos;", "'").replace("_apos;", "'")

    def batter_number(self):
        if self.is_sub():
            return StandardError("No batter for substitution event")
        else:
            return self._batter_number

    def text(self):
        return self._text.replace("&apos;", "'").replace("_apos;", "'")

    def title(self):
        if self.is_sub():
            return self._type
        else:
            return "{} #{} {}".format(self._type, self._batter_number, self._batter_name)

    ######################### GRAVEYARD #################################
    # TDH - May 2013
    # these methods are no longer used after we are scraping roster and starting lineup from the html

    # def game_rosters(self, base_away_players=None, base_home_players=None):
    #     """ return full list of all players in the game """
    #     away = self.root.find(".//{*}VisitingTeam")
    #     away_offense_d = [dict(e.items()) for e in away.find(".//{*}Offense").getchildren()]
    #     away_replaced_d = [dict(e.items()) for e in away.find(".//{*}ReplacedOffense").getchildren()]
    #     away_pitchers_d = [dict(e.items() + [("Position", "P")]) for e in away.find(".//{*}Pitchers").getchildren()]

    #     home = self.root.find(".//{*}HomeTeam")
    #     home_offense_d = [dict(e.items()) for e in home.find(".//{*}Offense").getchildren()]
    #     home_replaced_d = [dict(e.items()) for e in home.find(".//{*}ReplacedOffense").getchildren()]
    #     home_pitchers_d = [dict(e.items() + [("Position", "P")]) for e in home.find(".//{*}Pitchers").getchildren()]

    #     if base_away_players is None:
    #         away_roster = PlayerList()
    #     else:
    #         away_roster = base_away_players

    #     if base_home_players is None:
    #         home_roster = PlayerList()
    #     else:
    #         home_roster = base_home_players

    #     away_pitchers = self._make_players(player_dict_list=away_pitchers_d, team_id=self.away_team())
    #     away_offense = self._make_players(player_dict_list=away_offense_d + away_replaced_d, team_id=self.away_team())
    #     away_roster.update_players(away_offense + away_pitchers)

    #     home_pitchers = self._make_players(player_dict_list=home_pitchers_d, team_id=self.home_team())
    #     home_offense = self._make_players(player_dict_list=home_offense_d + home_replaced_d, team_id=self.home_team())
    #     home_roster.update_players(home_offense + home_pitchers)

    #     self._complete_player_profile(False, away_roster)
    #     self._complete_player_profile(True, home_roster)
    #     return away_roster, home_roster

    # def scrape_lineup_from_seq_xml(self, seq):
    #     """
    #     helper method for starting_lineupa method.
    #     given a sequence number, grabs the xml file, and pulls out the lineups from it
    #     """
    #     xml = self._get_pointstreak_xml(seq)
    #     root = lxml.etree.fromstring(xml)
    #     away = root.find(".//{*}VisitingTeam")
    #     away_offense = [dict(e.items()) for e in away.find(".//{*}Offense").getchildren()]
    #     away_defense = [dict(e.items()) for e in away.find(".//{*}Defense").getchildren()]
    #     away_pitchers = [dict(e.items()) for e in away.find(".//{*}Pitchers").getchildren()]
    #     home = root.find(".//{*}HomeTeam")
    #     home_offense = [dict(e.items()) for e in home.find(".//{*}Offense").getchildren()]
    #     home_defense = [dict(e.items()) for e in home.find(".//{*}Defense").getchildren()]
    #     home_pitchers = [dict(e.items()) for e in home.find(".//{*}Pitchers").getchildren()]

    #     away_offense_player_list = self._make_players(player_dict_list=away_offense)
    #     away_defense_player_list = self._make_players(player_dict_list=away_defense)

    #     if away_pitchers:
    #         starting_pitcher = self._make_pitcher(player_dict=away_pitchers[0])
    #         if starting_pitcher is not None:
    #             try:
    #                 away_defense_player_list.find_player_by_name(starting_pitcher.name)
    #                 away_defense_player_list.update_player(starting_pitcher)
    #             except KeyError:
    #                 away_defense_player_list.insert(0, starting_pitcher)

    #     home_offense_player_list = self._make_players(player_dict_list=home_offense)
    #     home_defense_player_list = self._make_players(player_dict_list=home_defense)

    #     if home_pitchers:
    #         starting_pitcher = self._make_pitcher(player_dict=home_pitchers[0])
    #         if starting_pitcher is not None:
    #             try:
    #                 home_defense_player_list.find_player_by_name(starting_pitcher.name)
    #                 home_defense_player_list.update_player(starting_pitcher)
    #             except KeyError:
    #                 home_defense_player_list.insert(0, starting_pitcher)
    #     return away_offense_player_list + away_defense_player_list, home_offense_player_list + home_defense_player_list

    # def starting_lineups(self, away_roster=None, home_roster=None):
    #     """
    #     scrape the starting lineup from the sequential point streak XMl files

    #     loop through the xml files until a complete lineup for both teams has been established
    #     """
    #     complete = False
    #     seq = 1
    #     away_lineup = Lineup()
    #     home_lineup = Lineup()

    #     while not complete:
    #         try:
    #             away_player_list, home_player_list = self.scrape_lineup_from_seq_xml(seq)

    #             for p in away_player_list:
    #                 if p.position not in away_lineup.position_dict() and p.name is not None:
    #                     try:
    #                         roster_player = away_roster.find_player_by_name(p.name)
    #                         roster_player.merge(p)
    #                         p = roster_player
    #                     except KeyError:
    #                         pass
    #                     away_lineup.update_player(p)
    #             for p in home_player_list:
    #                 if p.position not in home_lineup.position_dict() and p.name is not None:
    #                     try:
    #                         roster_player = home_roster.find_player_by_name(p.name)
    #                         roster_player.merge(p)
    #                         p = roster_player
    #                     except KeyError:
    #                         pass
    #                     home_lineup.update_player(p)

    #             try:
    #                 complete = home_lineup.is_complete(raise_reason=False)
    #             except LineupError, e:
    #                 logging.error(str(e) + "\nHome \n" + str(home_lineup))

    #             try:
    #                 complete &= away_lineup.is_complete(raise_reason=False)
    #             except LineupError, e:
    #                 logging.error(str(e) + "\nAway \n" + str(away_lineup))

    #         except lxml.etree.XMLSyntaxError:
    #             logger.error("Error parsing lineup from game %s seq %s" % (self.gameid, seq))
    #         seq += 1
    #         if seq > MAX_EVENTS_COUNT:
    #             # check each lineup for completeness, raising the reason for incomplete
    #             home_lineup.is_complete(raise_reason=True)
    #             away_lineup.is_complete(raise_reason=True)

    #     self._complete_player_profile(False, away_lineup)
    #     self._complete_player_profile(True, home_lineup)
    #     return away_lineup, home_lineup


    # def _make_pitcher(self, player_dict, team_id=None):
    #     new_player = Player(player_dict.get("Name"),
    #                         player_dict.get("Number"),
    #                         player_dict.get("Order"),
    #                         constants.P,
    #                         player_dict.get("Hand"),
    #                         iddict={"pointstreak": None},
    #                         team_id=team_id)
    #     if new_player.name is not None:
    #         return new_player
    #     else:
    #         return None

    # def _make_players(self, player_dict_list, team_id=None):
    #     out = PlayerList()
    #     for player_dict in player_dict_list:
    #         try:
    #             new_player = Player(player_dict.get("Name"),
    #                                 player_dict.get("Number"),
    #                                 player_dict.get("Order"),
    #                                 player_dict.get("Position"),
    #                                 player_dict.get("Hand"),
    #                                 iddict={"pointstreak": None},
    #                                 team_id=team_id)
    #             if new_player.name is not None:
    #                 out.add_player(new_player)
    #         except (AttributeError, KeyError):
    #             logger.error("making Player from dict = %s" % player_dict)
    #             raise
    #     return out
