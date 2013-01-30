import constants
import gamestate

import logging

logger = logging.getLogger("gamewrapper")
class GameWrapper:
    """
    GameWrap.  This class is a wrapper around the gamestate class.

    It allows gamestate instances to be swapped out without needing to re-hook the calls
    setup in a parser.
    """

    def __init__(self, game=None):
        self.set_game(game)
        # for autocomplete
        if False:
            self._game = gamestate.GameState()

    def set_game(self, game):
        self._game = game

    def pickoff(self, text, location, tokens):
        base = ' '.join(tokens[constants.PARSING.BASE])
        throw_position = tokens[constants.PARSE_PITCHING.THROW_POSITION]
        catch_position = tokens[constants.PARSE_PITCHING.CATCH_POSITION]
        self._game.pitch_pickoff_attempt(base, throw_position, catch_position)

    def swinging_strike(self, *args):
        self._game.pitch_swinging_strike()

    def called_strike(self, *args):
        self._game.pitch_called_strike()

    def ball(self, *args):
        self._game.pitch_ball()

    def dropped_foul(self, text, location, tokens):
        error = tokens.get(constants.PARSING.ERROR, None)
        error_position = tokens.get(constants.PARSING.POSITION, None)
        self._game.pitch_foul(True, error, error_position)

    def foul(self,  text, location, tokens):
        self._game.pitch_foul()

    def put_out(self, text, location, tokens):
        player_name = tokens[constants.PARSING.PLAYER][constants.PARSING_PLAYER.NAME]
        if type(player_name) == list:
            player_name = ' '.join(player_name)
        player_name = player_name.replace("&apos;","'")
        #print "PUTOUT", player_name
        description = tokens[constants.PARSING.DESCRIPTION]
        position = description.get(constants.PARSING.POSITION)
        logger.info(text)
        if constants.PARSING_OUTS.THROWN_OUT in description:
            self._game.out_thrown_out(player_name,
                                      description[constants.PARSING_OUTS.THROWN_OUT],
                                      constants.PARSING_OUTS.SACRIFICE in description,
                                      constants.PARSING_OUTS.DOUBLE_PLAY in description,
                                      constants.PARSING_OUTS.TRIPLE_PLAY in description
                                      )
        elif constants.PARSING_OUTS.FLY_OUT in description:
            self._game.out_fly_out(player_name,
                                   position,
                                   constants.PARSING_OUTS.SACRIFICE in description)
        elif constants.PARSING_OUTS.STRIKE_OUT in description:
            self._game.out_strike_out(player_name,
                                      constants.PARSING_OUTS.SWINGING in description)
        elif constants.PARSING_OUTS.CAUGHT_STEALING in description:
            self._game.out_caught_stealing(player_name, tokens,
                                           constants.PARSING_OUTS.DOUBLE_PLAY in description)
        elif constants.PARSING_OUTS.UNASSISTED in description or constants.PARSING_OUTS.LINE_DRIVE in description:
            self._game.out_unassisted(player_name,
                                      position,
                                      constants.PARSING_OUTS.FOUL in description)
        elif constants.PARSING_OUTS.POPUP in description:
            logger.info("POPUP")
            self._game.out_popup(player_name,
                                 position,
                                 constants.PARSING_OUTS.FOUL in description)
        else:
            logger.error("Unknown Putout Description" + str(description))
            self._game._out(player_name)
            #raise StandardError("Parsing Error from unknown putout description: " + ' '.join(tokens))

    def parse_offensive_sub(self, text, location, tokens):
        new_player_name = tokens[constants.PARSING.NEW_PLAYER][1:]
        replacing_name = tokens.get(constants.PARSING.REPLACING, [])
        
        if type(new_player_name) == list:
            new_player_name = ' '.join(new_player_name).strip() 
        if type(replacing_name) == list:
            replacing_name = ' '.join(replacing_name).strip() 

        if constants.PARSING.BASE in tokens.asDict():
            self._game.offensive_sub(new_player_name, replacing_name, pinch_runner=True, base=tokens[constants.PARSING.BASE])
        else:
            self._game.offensive_sub(new_player_name, replacing_name)

    def parse_defensive_sub(self, text, location, tokens):
        new_player_name = tokens[constants.PARSING.NEW_PLAYER][1:]
        replacing_name = tokens.get(constants.PARSING.REPLACING, [])# strip space to empty string if nothing there
        
        if type(new_player_name) == list:
            new_player_name = ' '.join(new_player_name).strip() 
        if type(replacing_name) == list:
            replacing_name = ' '.join(replacing_name).strip() 
        
        position = ' '.join(tokens.get(constants.PARSING.POSITION, [])).strip() # strip space to empty string if nothing there
        self._game.defensive_sub(new_player_name, replacing_name, position)

    def parse_advance(self, text, location, tokens):
        tdict = tokens.asDict()
        description = tokens[constants.PARSING.DESCRIPTION]
        player_name = tdict[constants.PARSING.PLAYER][1:]

        if type(player_name) == list:
            player_name = ' '.join(player_name)

        base = tdict["base"][0]
        self._advance(player_name, base, description)

    def parse_score(self, text, location, tokens):
        tdict = tokens.asDict()
        description = tokens[constants.PARSING.DESCRIPTION]
        player_name = tdict[constants.PARSING.PLAYER][1:]

        if type(player_name) == list:
            player_name = ' '.join(player_name)

        earned = constants.PARSING.EARNED in description
        base = 4
        self._advance(player_name, base, description, earned)

    def _advance(self, player_name, base, description, earned=True):
        if constants.PARSE_ADVANCE.STOLEN_BASE in description:
            self._game.advance_on_stolen_base(player_name, base)
        elif constants.PARSE_ADVANCE.WILD_PITCH in description:
            self._game.advance_on_wild_pitch(player_name, base)
        elif constants.PARSE_ADVANCE.PASS_BALL in description:
            self._game.advance_on_passed_ball(player_name, base)
        elif constants.PARSE_ADVANCE.THROW in description:
            self._game.advance_on_throw(player_name, base)
        elif constants.PARSE_ADVANCE.SINGLE in description:
            self._game.hit_single(player_name, location = description.get(constants.PARSING.LOCATION, None))
        elif constants.PARSE_ADVANCE.DOUBLE in description:
            self._game.hit_double(player_name, location = description.get(constants.PARSING.LOCATION, None))
        elif constants.PARSE_ADVANCE.TRIPLE in description:
            self._game.hit_triple(player_name, location = description.get(constants.PARSING.LOCATION, None))
        elif constants.PARSE_ADVANCE.HOME_RUN in description:
            self._game.hit_home_run(player_name, location = description.get(constants.PARSING.LOCATION, None))
        elif constants.PARSING.ERROR in description:
            self._game.advance_on_error(player_name,
                                        base,
                                        description[constants.PARSING.POSITION],
                                        description.get(constants.PARSING.ERROR_TYPE, None))
        elif constants.PARSE_ADVANCE.FIELDERS_CHOICE in description:
            self._game.advance_on_fielders_choice(player_name, base)
        elif constants.PARSE_ADVANCE.GROUND_RULE in description:
            self._game.advance_on_ground_rule(player_name, base)
        elif constants.PARSE_ADVANCE.HIT_BY_PITCH in description:
            self._game.advance_on_hit_by_pitch(player_name)
        elif constants.PARSE_ADVANCE.INTENTIONAL_WALK in description:
            self._game.advance_on_walk(player_name, intentional=True)
        elif constants.PARSE_ADVANCE.WALK in description:
            self._game.advance_on_walk(player_name, intentional=False)
        elif constants.PARSE_ADVANCE.DROPPED_THIRD_STRIKE in description:
            self._game.advance_on_dropped_third_strike(player_name)
        elif constants.PARSE_ADVANCE.PLAYER_NUM in description:
            batter_number = description.get(constants.PARSE_ADVANCE.PLAYER_NUM, None)
            self._game.advance_from_batter(player_name, base, batter_number)
        else:
            #raise StandardError("Parsing Error from unknown Advance description: " + ' '.join(description))
            logger.error("Unknown Advance Description" + str(description))
            self._game._advance_player(player_name, base, earned)

    def event_complete(self, *args):
        self._game._record_event()
