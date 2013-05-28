"""
a means to save games outside of their html state.

"""

import logging
import json
import os
from collections import OrderedDict

from lineup import Lineup, PlayerList, Player

# a hack for 2.x versiont o get the ordereddict objects to translate into json in the right order
#  see: http://stackoverflow.com/questions/4402491/custom-json-sort-keys-order-in-python
json.encoder.c_make_encoder = None

ERROR_KEY = "process_output"


class GameContainer:
    def __init__(self, cache_path, gameid=None, away_team=None, home_team=None):
        assert(cache_path is not None)
        self.gameid = gameid
        self.url = None
        self.home_team = home_team
        self.away_team = away_team
        self.list_of_halfs = []
        self.current_half = None
        self.cache_path = cache_path
        if away_team is None:
            self.load()
        self.errors = []

    def set_home_lineup(self, lineup):
        self.home_lineup = lineup

    def set_away_lineup(self, lineup):
        self.away_lineup = lineup

    def set_home_roster(self, roster):
        self.home_roster = roster

    def set_away_roster(self, roster):
        self.away_roster = roster

    def new_half(self):
        self.list_of_halfs.append([])
        self.current_half = self.list_of_halfs[-1]

    def add_event(self, title, text, batter):
        self.current_half.append(OrderedDict(title=title, batter=batter, text=text, inning=(len(self.list_of_halfs)+ 1)/2.0))

    def add_sub(self, title, text):
        self.current_half.append(OrderedDict(title=title, text=text, inning=(len(self.list_of_halfs)+ 1)/2.0))

    def save(self):
        d = OrderedDict()
        d["gameid"] = self.gameid
        d["url"] = self.url
        d["home_team"] = self.home_team
        d["away_team"] = self.away_team
        d["home_lineup"] = [p.as_odict() for p in self.home_roster if p.starter]
        d["home_roster"] = [p.as_odict() for p in self.home_roster if not p.starter]
        d["away_lineup"] = [p.as_odict() for p in self.away_roster if p.starter]
        d["away_roster"] = [p.as_odict() for p in self.away_roster if not p.starter]
        d["list_of_halfs"] = self.list_of_halfs
        d["general_errors"] = []
        for e in self.errors:
            try:
                half_index = int((e.get("inning") + 0.5 * int(e.get("bottom"))) * 2 - 2)
                event_errors = d["list_of_halfs"][half_index][e.get("event_num")].get(ERROR_KEY, [])
                event_errors.append(e.get("message"))
                d["list_of_halfs"][half_index][e.get("event_num")][ERROR_KEY] = event_errors
            except IndexError:
                d["general_errors"].append(e.get("message"))
        with open(os.path.join(self.cache_path, "gc_{}.json".format(self.gameid)), 'w') as f:
            json.dump(d,
                      f,
                      #sort_keys=True,
                      indent=4,
                      separators=(', ', ': '))

    def load(self, remove_errors=True):
        with open(os.path.join(self.cache_path, "gc_{}.json".format(self.gameid)), 'r') as f:
            d = json.load(f, object_pairs_hook=OrderedDict)

        self.away_lineup = Lineup()
        self.home_lineup = Lineup()

        self.away_roster = PlayerList()
        self.home_roster = PlayerList()

        skip = ["bat_stats", "pitch_stats"]

        for playerd in d["home_lineup"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                if key not in skip:
                    setattr(p, key, val)
            self.home_lineup.append(p)
            self.home_roster.append(p)

        for playerd in d["away_lineup"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                if key not in skip:
                    setattr(p, key, val)
            self.away_lineup.append(p)
            self.away_roster.append(p)

        for playerd in d["home_roster"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                if key not in skip:
                    setattr(p, key, val)
            self.home_roster.append(p)

        for playerd in d["away_roster"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                if key not in skip:
                    setattr(p, key, val)
            self.away_roster.append(p)

        self.gameid = d["gameid"]
        self.url = d.get("url")
        self.home_team = d["home_team"]
        self.away_team = d["away_team"]
        self.list_of_halfs = d["list_of_halfs"]
        if remove_errors:
            for h in self.list_of_halfs:
                for e in h:
                    if ERROR_KEY in e:
                        del(e[ERROR_KEY])

        self.current_half = self.list_of_halfs[0]

    def halfs(self):
        for h in self.list_of_halfs:
            yield h

    def log_error(self, inning, bottom, event_num, message):
        self.errors.append(dict(inning=inning, bottom=bottom, event_num=event_num, message=message))


class GameContainerLogHandler(logging.Handler):
    """
    A handler class which allows logs to get inserted into a game container
    """
    def __init__(self, game_container):
        logging.Handler.__init__(self)
        self.gc = game_container
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        self.setFormatter(formatter)
        self.setLevel(logging.INFO)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.gc.log_error(record.inning, record.is_bottom, record.event_num, msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
