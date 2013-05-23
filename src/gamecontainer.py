"""
a means to save games outside of their html state.

"""

import json
import os
from collections import OrderedDict

from lineup import Lineup, PlayerList, Player

# a hack for 2.x versiont o get the ordereddict objects to translate into json in the right order
#  see: http://stackoverflow.com/questions/4402491/custom-json-sort-keys-order-in-python
json.encoder.c_make_encoder = None



class GameContainer:
    def __init__(self, cache_path, gameid=None, away_team=None, home_team=None):
        assert(cache_path is not None)
        self.gameid = gameid
        self.home_team = home_team
        self.away_team = away_team
        self.list_of_halfs = []
        self.current_half = None
        self.cache_path = cache_path
        if away_team is None:
            self.load()

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
        self.current_half.append(dict(title=title, text=text, batter=batter, inning=(len(self.list_of_halfs)+ 1)/2.0))

    def add_sub(self, title, text):
        self.current_half.append(dict(title=title, text=text, sub="_sub_", inning=(len(self.list_of_halfs)+ 1)/2.0))

    def save(self):
        d = OrderedDict()
        d["gameid"] = self.gameid
        d["home_team"] = self.home_team
        d["away_team"] = self.away_team
        d["home_lineup"] = [p.as_odict() for p in self.home_lineup]
        d["away_lineup"] = [p.as_odict() for p in self.away_lineup]
        d["home_roster"] = [p.as_odict() for p in self.home_roster if p not in self.home_lineup]
        d["away_roster"] = [p.as_odict() for p in self.away_roster if p not in self.away_lineup]
        d["list_of_halfs"] = self.list_of_halfs

        with open(os.path.join(self.cache_path, "gc_{}.json".format(self.gameid)), 'w') as f:
            json.dump(d,
                      f,
                      #sort_keys=True,
                      indent=4,
                      separators=(', ', ': '))


    def load(self):
        with open(os.path.join(self.cache_path, "gc_{}.json".format(self.gameid)), 'r') as f:
            d = json.load(f)

        self.away_lineup = Lineup()
        self.home_lineup = Lineup()

        self.away_roster = PlayerList()
        self.home_roster = PlayerList()

        for playerd in d["home_lineup"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                setattr(p, key, val)
            self.home_lineup.append(p)
            self.home_roster.append(p)

        for playerd in d["away_lineup"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                setattr(p, key, val)
            self.away_lineup.append(p)
            self.away_roster.append(p)

        for playerd in d["home_roster"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                setattr(p, key, val)
            self.home_roster.append(p)

        for playerd in d["away_roster"]:
            p = Player(playerd["name"])
            for key, val in playerd.items():
                setattr(p, key, val)
            self.away_roster.append(p)

        self.gameid = d["gameid"]
        self.home_team = d["home_team"]
        self.away_team = d["away_team"]
        self.list_of_halfs = d["list_of_halfs"]
        self.current_half = self.list_of_halfs[0]


    def halfs(self):
        for h in self.list_of_halfs:
            yield h