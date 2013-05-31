"""
A class matching the gamewrapper interface that is used to pull substitutions from the parser

give it two lineups, run it through the subs of the game, and it will give back the starting lineups
"""

import constants
from gamewrapper import GameWrapper

class SubTracker(GameWrapper):
    """docstring for SubTracker"""

    def __init__(self, lineup):
        GameWrapper.__init__(self)
        self.lineup = lineup
        for p in self.lineup:
            p.starting_position = p.all_positions
        # starting positions begins as all possible, but we will eliminate options
        self._found_starting_pitcher = False

    def parse_offensive_sub(self, text, location, tokens):
        new_player_name = tokens[constants.PARSING.NEW_PLAYER][1:]
        replacing_name = tokens.get(constants.PARSING.REPLACING, [])

        if type(new_player_name) == list:
            new_player_name = ' '.join(new_player_name).strip()
        if type(replacing_name) == list:
            replacing_name = ' '.join(replacing_name).strip()

        #if constants.PARSING.BASE in tokens.asDict():
        #    self._game.offensive_sub(new_player_name, replacing_name, pinch_runner=True, base=tokens[constants.PARSING.BASE])
        #else:
        #    self._game.offensive_sub(new_player_name, replacing_name)

    def parse_pitching_sub(self, text, location, tokens):
        tokens[constants.PARSING.POSITION] = 'p'
        self.parse_defensive_sub(text, location, tokens)

    def parse_defensive_sub(self, text, location, tokens):
        new_player_name = tokens.get(constants.PARSING.NEW_PLAYER, {}).get(constants.PARSING_PLAYER.NAME, [])
        replacing_name = tokens.get(constants.PARSING.REPLACING, [])
        if type(replacing_name) == dict:
            replacing_name = replacing_name.get(constants.PARSING_PLAYER.NAME, [])
        if type(new_player_name) == list:
            new_player_name = ' '.join(new_player_name).strip()
        if type(replacing_name) == list:
            replacing_name = ' '.join(replacing_name).strip()
        position = ' '.join(tokens.get(constants.PARSING.POSITION, [])).strip()  # strip space to empty string if nothing there

        if position:
            position = constants.POSITION_LOOKUP[position.lower()]
        else:
            return

        # if position == 'P':
        #     if self._found_starting_pitcher:
        #         return
        #     else:
        #         # replacing_name is the starter

        #         for i, player, pos in zip(range(len(self.lineup)), self.lineup, self.starting_position):
        #             if player.name == replacing_name:
        #                 self._found_starting_pitcher = True
        #                 self.starting_position[i] = ['P']
        #             else:
        #                 if 'P' in pos:
        #                     self.starting_position[i].remove('P')
        # else:
        # if this is a movement of a starting player, eliminate this position from starting possibles
        for player in self.lineup:
            if player.name == new_player_name:
                # makes sure to not eliminate the only remaining position.  if a player moves away and
                # back to a starting position, this could happen
                if len(player.starting_position) > 1:
                    player.starting_position.remove(position)

