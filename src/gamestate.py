"""
GameState is a python class to represent the ongoing gamestate
as parsed by a play by play parser.  The attributes of this class
have a one-to-one relationship with the Chadwick Event Descriptor.

Therefore, at any time, this class may be added as a line in a SQL event database
"""

import logging
logger = logging.getLogger("gamestate")
import constants

from bases import Bases
from models import event
import eventfields
from lineup import LineupError

MODEL_LOOKUP_DICT = eventfields.lookup_dict()


class GameState:
    def __init__(self):
        self.game_id = None
        self.visiting_team = None

        self.inning = 0
        self.bat_home_id = 0
        self.outs = 0
        self.balls = 0
        self.strikes = 0
        self.pitch_sequence = ''
        self.visitor_score = 0
        self.home_score = 0

        self.batter = None
        self.batter_hand = None
        self.result_batter = None  #TODO: result batter
        self.result_batter_hand = None  #TODO: result batter hand

        self.pitcher = None
        self.pitcher_hand = None
        self.result_pitcher = None  #TODO: result pitcher
        self.result_pitcher_hand = None  #TODO: result pitcher hand

        self.catcher = None
        self.first_baseman = None
        self.second_baseman = None
        self.third_baseman = None
        self.shortstop = None
        self.left_fielder = None
        self.center_fielder = None
        self.right_fielder = None

        self.runner_on_first = None
        self.runner_on_second = None
        self.runner_on_third = None

        self.event_text = ''
        self.leadoff_flag = False
        self.pinch_hit_flag = False
        self.defensive_position = None
        self.lineup_position = None

        self.event_type = None  #TODO: implement event_type

        self.batter_event_flag = False  # True in near all cases except recording stolen bases or caught stealing events
        self.official_time_at_bat_flag = False  # true for plate appearance that don't show (BB, HBP, SF, SH, interferance, obstruction)
        self.hit_value = 0

        self.sacrifice_hit_flag = False
        self.sacrifice_fly_flag = False
        self.outs_on_play = 0
        self.double_play_flag = False
        self.triple_play_flag = False
        self.rbi_on_play = 0
        self.wild_pitch_flag = False
        self.passed_ball_flag = False

        self.fielded_by = 0
        self.batted_ball_type = None  #TODO: getting batted_ball_type with point streak?
        self.bunt_flag = False  #TODO: getting bunt_flag with point streak?
        self.foul_flag = False
        self.hit_location = ''
        self.number_of_errors = 0

        self.first_error_player = None
        self.first_error_type = None
        self.second_error_player = None
        self.second_error_type = None
        self.third_error_player = None
        self.third_error_type = None

        self.batter_destination = None
        self.runner_on_first_destination = None
        self.runner_on_second_destination = None
        self.runner_on_third_destination = None

        self.play_on_batter = None
        self.play_on_runner_on_first = None
        self.play_on_runner_on_second = None
        self.play_on_runner_on_third = None

        self.stolen_base_for_runner_on_first = False
        self.stolen_base_for_runner_on_second = False
        self.stolen_base_for_runner_on_third = False

        self.caught_stealing_for_runner_on_first = False
        self.caught_stealing_for_runner_on_second = False
        self.caught_stealing_for_runner_on_third = False

        self.pickoff_of_runner_on_first = False
        self.pickoff_of_runner_on_second = False
        self.pickoff_of_runner_on_third = False

        self.pitcher_charged_with_runner_on_first = None
        self.pitcher_charged_with_runner_on_second = None
        self.pitcher_charged_with_runner_on_third = None

        self.new_game_flag = True
        self.end_game_flag = False

        self.pinch_runner_on_first = None
        self.pinch_runner_on_second = None
        self.pinch_runner_on_third = None

        self.runner_removed_for_pinch_runner_on_first = None
        self.runner_removed_for_pinch_runner_on_second = None
        self.runner_removed_for_pinch_runner_on_third = None

        self.batter_removed_for_pinch_hitter = None
        self.position_of_batter_removed_for_pinch_hitter = None

        self.fielder_with_first_putout = None
        self.fielder_with_second_putout = None
        self.fielder_with_third_putout = None

        self.fielder_with_first_assist = None
        self.fielder_with_second_assist = None
        self.fielder_with_third_assist = None
        self.fielder_with_fourth_assist = None
        self.fielder_with_fifth_assist = None
        self.event_number = 1

        # Extended Fields
        self.description = None
        self.home_team_id = 0
        self.batting_team_id = None
        self.fielding_team_id = None
        self.half_inning = 0  # (differs_from_batting_team_if_home_team_bats_first)
        self.start_of_half_inning_flag = False
        self.end_of_half_inning_flag = False
        self.score_for_team_on_offense = 0
        self.score_for_team_on_defense = 0
        self.runs_scored_in_this_half_inning = 0
        self.number_of_plate_appearances_in_game_for_team_on_offense = None
        self.number_of_plate_appearances_in_inning_for_team_on_offense = None
        self.start_of_plate_appearance_flag = False
        self.truncated_plate_appearance_flag = False
        self.base_state_at_start_of_play = None
        self.base_state_at_end_of_play = None
        self.batter_is_starter_flag = False
        self.result_batter_is_starter_flag = False
        self.id_of_the_batter_on_deck = None
        self.id_of_the_batter_in_the_hold = None
        self.pitcher_is_starter_flag = False
        self.result_pitcher_is_starter_flag = False
        self.defensive_position_of_runner_on_first = None
        self.lineup_position_of_runner_on_first = None
        self.event_number_on_which_runner_on_first_reached_base = None
        self.defensive_position_of_runner_on_second = None
        self.lineup_position_of_runner_on_second = None
        self.event_number_on_which_runner_on_second_reached_base = None
        self.defensive_position_of_runner_on_third = None
        self.lineup_position_of_runner_on_third = None
        self.event_number_on_which_runner_on_third_reached_base = None
        self.responsible_catcher_for_runner_on_first = None
        self.responsible_catcher_for_runner_on_second = None
        self.responsible_catcher_for_runner_on_third = None
        self.number_of_balls_in_plate_appearance = None
        self.number_of_called_balls_in_plate_appearance = None
        self.number_of_intentional_balls_in_plate_appearance = None
        self.number_of_pitchouts_in_plate_appearance = None
        self.number_of_pitches_hitting_batter_in_plate_appearance = None
        self.number_of_other_balls_in_plate_appearance = None
        self.number_of_strikes_in_plate_appearance = None
        self.number_of_called_strikes_in_plate_appearance = None
        self.number_of_swinging_strikes_in_plate_appearance = None
        self.number_of_foul_balls_in_plate_appearance = None
        self.number_of_balls_in_play_in_plate_appearance = None
        self.number_of_other_strikes_in_plate_appearance = None
        self.number_of_runs_on_play = None
        self.id_of_player_fielding_batted_ball = None
        self.force_play_at_second_flag = False
        self.force_play_at_third_flag = False
        self.force_play_at_home_flag = False
        self.batter_safe_on_error_flag = False
        self.fate_of_batter = None
        self.fate_of_runner_on_first = None
        self.fate_of_runner_on_second = None
        self.fate_of_runner_on_third = None
        self.runs_scored_in_half_inning_after_this_event = 0
        self.fielder_with_sixth_assist = None
        self.fielder_with_seventh_assist = None
        self.fielder_with_eighth_assist = None
        self.fielder_with_ninth_assist = None
        self.fielder_with_tenth_assist = None
        self.unknown_fielding_credit_flag = False
        self.uncertain_play_flag = False

        #=======================================================================
        # Non Model attributes
        #=======================================================================
        self._next_batter_pinch = False
        self._next_batter_leadoff = False
        self._home_place_in_batting_order = 1  #always start with leadoff batter
        self._away_place_in_batting_order = 1  #always start with leadoff batter
        self._current_place_in_order = 1
        self._last_batter = None

        # These pending attributes allow us to make updates to the gamestate but
        # hold off applying it to attributes until after event is complete
        self._bases = Bases()

        self._pending_pitcher_charged_with_runner_on_first = None
        self._pending_pitcher_charged_with_runner_on_second = None
        self._pending_pitcher_charged_with_runner_on_third = None

        self._advancing_event_text = ''
        self._last_event = None
        self._pending_runner_event = None

        # the whole reason this class exists is to fill this list!
        self.event_list = []

    #------------------------------------------------------------------------------
    # GAME SETUP
    #------------------------------------------------------------------------------

    def set_home_lineup(self, lineup):
        """ set home starting lineup with Lineup object """
        self.home_lineup = lineup
        for p in self.home_lineup:
            p.atbats = 0

    def set_away_lineup(self, lineup):
        """ set away starting lineup with Lineup object """
        self.away_lineup = lineup
        for p in self.away_lineup:
            p.atbats = 0

    def set_home_roster(self, roster):
        """ set all home players appearing in this game"""
        self.home_roster = roster

    def set_away_roster(self, roster):
        """ set all away players appearing in this game"""
        self.away_roster = roster

    #------------------------------------------------------------------------------
    # Database Management
    #------------------------------------------------------------------------------

    def events(self):
        for e in self.event_list:
            yield e

    def _get_state_as_event_model(self):
        newmodel = event.Event()
        for key, modelattribute in MODEL_LOOKUP_DICT.items():
            newmodel.__dict__[modelattribute] = self.__dict__[key]
        return newmodel

    def _record_event(self, batting_event=True):
        """
        send event to database
        normally batting events, but in the case of runner events,
        send new record to database with batting event = False
        ie.  stolen base, caught stealing, balk, pickoff, out advancing, wild pitch, passed ball
        """

        self._record_any_pending_runner_event()
        self.batter_event_flag = batting_event
        if batting_event:
            self.official_time_at_bat_flag = self._batting_event_is_official

        self.event_text += self._advancing_event_text
        self._last_event = self._get_state_as_event_model()
        self.event_list.append(self._last_event)
        logger.debug(">-- APPEND EVENT --<")
        self._apply_pending_base_runner_positions()
        self._reset_flags()

    def _record_any_pending_runner_event(self):
        if self._pending_runner_event:
            self._pending_runner_event = False
            self._record_event(batting_event=False)

    def set_previous_event_as_game_end(self):
        # in case last event was a runner event, it is still pending, so send it
        self._record_any_pending_runner_event()
        self._last_event.GAME_END_FL = True

    #------------------------------------------------------------------------------
    # UTILITIES
    #------------------------------------------------------------------------------

    def _update_lineups_and_fielders(self):
        """ set with a list of players in numbered position order """
        if self.bat_home_id:
            self.batting_lineup = self.home_lineup
            self.fielding_lineup = self.away_lineup
            self._current_place_in_order = self._home_place_in_batting_order
        else:
            self.batting_lineup = self.away_lineup
            self.fielding_lineup = self.home_lineup
            self._current_place_in_order = self._away_place_in_batting_order
        self._update_fielders()

    def _update_fielders(self):
        fielder_pos_dict = self.fielding_lineup.position_dict()
        self.pitcher = fielder_pos_dict['P']
        self.result_pitcher = self.pitcher
        player_pitcher = self.fielding_lineup.find_player_by_name(self.pitcher)
        self.pitcher_hand = player_pitcher.hand
        self.result_pitcher_hand = self.pitcher_hand
        self.catcher = fielder_pos_dict['C']
        self.first_baseman = fielder_pos_dict['1B']
        self.second_baseman = fielder_pos_dict['2B']
        self.third_baseman = fielder_pos_dict['3B']
        self.shortstop = fielder_pos_dict['SS']
        self.left_fielder = fielder_pos_dict['LF']
        self.center_fielder = fielder_pos_dict['CF']
        self.right_fielder = fielder_pos_dict['RF']

    def _current_batting_lineup(self):
        if self.bat_home_id:
            return self.home_lineup
        else:
            return self.away_lineup

    def _current_batting_roster(self):
        if self.bat_home_id:
            return self.home_roster
        else:
            return self.away_roster

    def _current_fielding_lineup(self):
        if self.bat_home_id:
            return self.away_lineup
        else:
            return self.home_lineup

    def _current_fielding_roster(self):
        if self.bat_home_id:
            return self.away_roster
        else:
            return self.home_roster

    def _increment_batting_order(self):
        # if the order was incremented for this batter already, don't
        # this occurs in the case of a runner advancing twice (ie. after an error at first) in their atbat play
        if self._last_batter == self.batter:
            return
        else:
            self._last_batter = self.batter
            if self.bat_home_id:
                self._home_place_in_batting_order += 1
                if self._home_place_in_batting_order > 9:
                    self._home_place_in_batting_order = 1
                self._current_place_in_order = self._home_place_in_batting_order
            else:
                self._away_place_in_batting_order += 1
                if self._away_place_in_batting_order > 9:
                    self._away_place_in_batting_order = 1
                self._current_place_in_order = self._away_place_in_batting_order
            # increment the atbat count
            self._current_batting_lineup().find_player_by_name(self.batter).atbats += 1

    def _reset_flags(self):
        "call this after writing out an event"
        # this only gets send once per game
        if self.new_game_flag:
            self.new_game_flag = False

        # reset any pinch runner flags
        self.pinch_runner_on_first = False
        self.pinch_runner_on_second = False
        self.pinch_runner_on_third = False

        self.runner_removed_for_pinch_runner_on_first = False
        self.runner_removed_for_pinch_runner_on_second = False
        self.runner_removed_for_pinch_runner_on_third = False

        self.play_on_batter = None
        self.play_on_runner_on_first = None
        self.play_on_runner_on_second = None
        self.play_on_runner_on_third = None
            
        self.fielder_with_first_putout = None
        self.fielder_with_second_putout = None
        self.fielder_with_third_putout = None

        self.fielder_with_first_assist = None
        self.fielder_with_second_assist = None
        self.fielder_with_third_assist = None
        self.fielder_with_fourth_assist = None
        self.fielder_with_fifth_assist = None
        self.fielder_with_sixth_assist = None
        self.fielder_with_seventh_assist = None
        self.fielder_with_eighth_assist = None
        self.fielder_with_ninth_assist = None
        self.fielder_with_tenth_assist = None

        self.event_text = ''
        self._advancing_event_text = ''
        self.event_number += 1

    def _apply_pending_base_runner_positions(self):
        """
        move all pending runner positions to their new locations

        call this method after sending the current event to the database
        this is because the runner_on_* attributes indicate the positions of runners
        at the beginning of a given event
        """

        self.runner_on_first, self.runner_on_second, self.runner_on_third = self._bases.runner_names()

        if self.runner_on_first is not None:
            self.pitcher_charged_with_runner_on_first = self._pending_pitcher_charged_with_runner_on_first
        else:
            self.pitcher_charged_with_runner_on_first = None
        if self.runner_on_second is not None:
            self.pitcher_charged_with_runner_on_second = self._pending_pitcher_charged_with_runner_on_second
        else:
            self.pitcher_charged_with_runner_on_second = None
        if self.runner_on_third is not None:
            self.pitcher_charged_with_runner_on_third = self._pending_pitcher_charged_with_runner_on_third
        else:
            self.pitcher_charged_with_runner_on_third = None

    def get_half_string(self):
        """ return 'Top' or 'Bottom' for string formatting"""
        if self.half_inning:
            return "Bottom"
        else:
            return "Top"

    def inning_string(self):
        return "Game {}: {} of the {}".format(self.game_id, self.get_half_string(), self.inning)

    def lookup_position(self, pos):
        """
        return position character code ie. P, C, 1B, 2B ... CF
        """
        return constants.POSITION_LOOKUP[str(pos).lower()]

    def lookup_position_num(self, pos):
        """
        return position number: 1 - 9
        """
        return constants.POSITION_CODES[self.lookup_position(pos)]

    #------------------------------------------------------------------------------
    #  NEW CALLS
    #------------------------------------------------------------------------------
    def new_batter(self, batter):
        if batter == self.batter:
            logger.warning("Same batter twice: {}.  game {} {} of the {}".format(batter, self.game_id, self.get_half_string(), self.inning))
            return
        self.batter = batter
        self.result_batter = batter
        self.balls = 0
        self.strikes = 0
        self.outs_on_play = 0
        self.hit_value = 0
        self.pitch_sequence = ''
        self.event_text = ''
        self.sacrifice_hit_flag = False
        self.sacrifice_fly_flag = False
        self.double_play_flag = False
        self.triple_play_flag = False
        self.rbi_on_play = 0
        self.wild_pitch_flag = False
        self.passed_ball_flag = False
        self.fielded_by = 0
        self.bunt_flag = False
        self.foul_flag = False
        self.batter_destination = None
        self.runner_on_first_destination = None
        self.runner_on_second_destination = None
        self.runner_on_third_destination = None
        self.hit_location = ''
        self.number_of_errors = 0
        self.first_error_player = None
        self.first_error_type = None
        self.second_error_player = None
        self.second_error_type = None
        self.third_error_player = None
        self.third_error_type = None
        self.batter_event_flag = False  # set this to False for any events sent to database before event is complete
        self.official_time_at_bat_flag = False
        self._batting_event_is_official = True # this is guilty until proven innocent
        logger.info("-> %s to bat" % batter)

        # If this the first batter in a new half, swap the lineups
        # we wait to perform this swap in order to allow any defensive substitutions or moves
        # to be swapped at the beginning of the half.  this way we know all positions are filled.
        # offensive subs such as pinch runners/hitters don't have defensive positions until start of next half
        if self._next_batter_leadoff:
            self._update_lineups_and_fielders()

        try:
            batter_player = self._current_batting_lineup().find_player_by_name(self.batter)
            assert(batter_player.order == self._current_place_in_order)

        except KeyError:
            # Player not in lineup
            logger.warning(self.batter + " not found in lineup for atbat")
            try:
                batter_player = self._current_batting_roster().find_player_by_name(self.batter)
                replacing_player = self._current_batting_lineup().find_player_by_order(self._current_place_in_order)
                logger.warning("Used roster for auto-substitution of %s for %s" % (batter_player.name, replacing_player.name))
                self.offensive_sub(batter_player.name, replacing_player.name)
                # normally in an offensive sub, the player position would be PH
                # in the case of an auto sub, we are going to just that player the position of the old player
                # this is because there likely wont be a defensive sub either to put this new player in the correct position
                batter_player.position = replacing_player.position

            except KeyError:
                raise StandardError("Auto Replace Failed.  %s not found in roster" % self.batter)
        except AssertionError:
            # Player order doesn't match expected order
            logger.warning("%s %s doesn't match expected order %s" % (batter_player.name, batter_player.order, self._current_place_in_order))
            if batter_player.atbats == 0:
                swap_with_player = self._current_batting_lineup().find_player_by_order(self._current_place_in_order)
                if swap_with_player.atbats == 0:
                    swap_with_player.order = batter_player.order
                    batter_player.order = self._current_place_in_order
                    logger.warning("Used roster for auto-order swap of %s for %s" % (batter_player.name, swap_with_player.name))
                else:
                    raise
            else:
                raise
        self.defensive_position = batter_player.position
        self.lineup_position = batter_player.order
        self.batter_hand = batter_player.hand
        self.result_batter_hand = batter_player.hand
        if self._next_batter_leadoff:
            self._next_batter_leadoff = False
            self.leadoff_flag = True
        else:
            self.leadoff_flag = False

        if self._next_batter_pinch:
            self._next_batter_pinch = False
            self.pinch_hit_flag = True
        else:
            self.pinch_hit_flag = False

    def new_inning(self):
        self.inning += 1
        self.new_half()

    def new_half(self):
        self.outs = 0
        self.runner_on_first = None
        self.runner_on_second = None
        self.runner_on_third = None

        self._bases.clear()

        self._pending_pitcher_charged_with_runner_on_first = None
        self._pending_pitcher_charged_with_runner_on_second = None
        self._pending_pitcher_charged_with_runner_on_third = None

        if self.inning != 0:
            self.half_inning = int(not self.half_inning)
            self.bat_home_id = int(not self.bat_home_id)
            if self.half_inning == constants.TOP:
                self.inning += 1
        else:
            self.inning = 1
        self._next_batter_leadoff = True

        #self._update_lineups_and_fielders()
        #NOTE: lineups will be swapped when the first batter is called.
        # this allows any defensive subs at the beginning of the inning to
        # take place before we assign the new positions and confirm all positions
        # are accounted for to be performed prior to the first batter

        logger.info("====================== {half} of the {inning} =====================".format(
                                                                                      inning=self.inning,
                                                                                      half=self.get_half_string()
                                                                                      )
                    )

    #------------------------------------------------------------------------------
    # PLAY ERRORS
    #------------------------------------------------------------------------------

    def error(self, error_position, error_type):
        position_code = self.lookup_position_num(error_position)
        self.number_of_errors += 1
        if self.number_of_errors == 1:
            self.first_error_player = position_code
            self.first_error_type = error_type
        elif self.number_of_errors == 2:
            self.second_error_player = position_code
            self.second_error_type = error_type
        elif self.number_of_errors == 3:
            self.third_error_player = position_code
            self.third_error_type = error_type
        

    #------------------------------------------------------------------------------
    #  PITCHES
    #------------------------------------------------------------------------------

    def pitch_ball(self):
        self._record_any_pending_runner_event()
        self.balls += 1
        self.pitch_sequence += constants.PITCH_CHARS.BALL
        logger.debug("Ball")

    def pitch_called_strike(self):
        self._record_any_pending_runner_event()
        self.strikes += 1
        self.pitch_sequence += constants.PITCH_CHARS.CALLED_STRIKE
        logger.debug("Called Strike")

    def pitch_swinging_strike(self):
        self._record_any_pending_runner_event()
        self.strikes += 1
        self.pitch_sequence += constants.PITCH_CHARS.SWINGING_STRIKE
        logger.debug("Swinging Strike")

    def pitch_foul(self, dropped=False, error=None, error_position=0):
        self._record_any_pending_runner_event()
        if self.strikes < 2:
            self.strikes += 1
        self.pitch_sequence += constants.PITCH_CHARS.FOUL
        if dropped and (error is not None):
            self.error(error_position, 'F')
        #TODO: how could I include this FOUL_ERROR?
        #self.event_type = constants.EVENT_CODE.FOUL_ERROR
        logger.debug("Foul")

    def pitch_pickoff_attempt(self, base, thrower_position, catcher_position):
        """
        record a pickoff attempt by pitcher

        args:
        base: 1, 2, or 3: the base where PO throw went
        """
        self._record_any_pending_runner_event()
        logger.debug("Pickoff at {}, {} to {}".format(base, thrower_position, catcher_position))
        base_num = constants.BASE_LOOKUP[base]
        if base_num not in [1, 2, 3]:
            raise StandardError("pickoff base not a valid argument (1, 2, or 3)")
        thrower = self.lookup_position(thrower_position)
        if thrower == 'C':
            self.pitch_sequence += constants.PITCH_CHARS.FOLLOWING_PICKOFF_THROW_BY_THE_CATCHER
        self.pitch_sequence += str(base_num)

    #------------------------------------------------------------------------------
    # OUTS
    #------------------------------------------------------------------------------

    def _out(self, player_name):
        self.outs += 1
        self.outs_on_play += 1

        if self.batter != player_name:
            self._bases.remove(player_name)

        if self.batter == player_name:
            self._increment_batting_order()

        if self.outs > 3:
            raise StandardError("Recorded over 3 outs")            
        logger.info("{} Put Out.".format(player_name))
        
    def _credit_putout_to_fielder(self, position_num):
        if self.fielder_with_first_putout is None:
            self.fielder_with_first_putout = position_num
        elif self.fielder_with_second_putout is None:
            self.fielder_with_second_putout = position_num
        else:
            self.fielder_with_third_putout = position_num

    def _credit_assist_to_fielder(self, position_num, assist_num):
        if assist_num == 1:
            self.fielder_with_first_assist = position_num
        elif assist_num == 2:
            self.fielder_with_second_assist = position_num
        elif assist_num == 3:
            self.fielder_with_third_assist = position_num
        elif assist_num == 4:
            self.fielder_with_fourth_assist = position_num
        elif assist_num == 5:
            self.fielder_with_fifth_assist = position_num
        elif assist_num == 6:
            self.fielder_with_sixth_assist = position_num
        elif assist_num == 7:
            self.fielder_with_seventh_assist = position_num
        elif assist_num == 8:
            self.fielder_with_eighth_assist = position_num
        elif assist_num == 9:
            self.fielder_with_ninth_assist = position_num
        elif assist_num == 10:
            self.fielder_with_tenth_assist = position_num
        else:
            raise ValueError("Error trying to credit fielder {} with assist number {}".format(position_num, assist_num))

    def _credit_fielders_with_out(self, player_name, fielders):
        # catch case of fields coming in as a string of digits, for example ['543']
        if len(fielders) == 1:
            if len(str(fielders)) > 1:
                fielders = list(str(fielders[0]))
        logger.info("Fielders {}".format(fielders))
        fielders = [self.lookup_position_num(pos) for pos in fielders]
        self.fielded_by = fielders[0]
        play_string = ''.join([str(p) for p in fielders[-2:]])
        if self.batter == player_name:
            self.play_on_batter = play_string
        elif player_name == self.runner_on_first:
            self.play_on_runner_on_first = play_string
        elif player_name == self.runner_on_second:
            self.play_on_runner_on_second = play_string
        elif player_name == self.runner_on_third:
            self.play_on_runner_on_third = play_string

        # credit the final fielder in the list with the out
        self._credit_putout_to_fielder(fielders[-1])

        current_assist_num = 1
        while current_assist_num < len(fielders) and current_assist_num <= constants.MAX_ASSIST_COUNT:
            position_num = fielders[-(current_assist_num + 1)]
            self._credit_assist_to_fielder(position_num, current_assist_num)
            current_assist_num += 1

    def out_thrown_out(self, player_name, fielders, sacrifice=False, double_play=False, triple_play=False, unassisted=False):
        """ throw out a player

        player_name - name of the player put out
        fielders - the string of the position players who did it. ie. "3U" "64" "543"
        """

        self._record_any_pending_runner_event()
        if self.batter == player_name:
            self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        self.sacrifice_hit_flag = sacrifice
        self.double_play_flag = double_play
        self.triple_play_flag = triple_play
        self._credit_fielders_with_out(player_name, fielders)
        self.event_text += "X" + '(' + ''.join([str(p) for p in fielders]) + ')'
        self.event_type = constants.EVENT_CODE.GENERIC_OUT
        self._out(player_name)
        if sacrifice:
            self._batting_event_is_official = False

    def out_caught_stealing(self, runner_name, fielders, double_play=False):
        self._record_any_pending_runner_event()
        if runner_name == self.runner_on_first:
            self.caught_stealing_for_runner_on_first = True
        elif runner_name == self.runner_on_second:
            self.caught_stealing_for_runner_on_second = True
        elif runner_name == self.runner_on_third:
            self.caught_stealing_for_runner_on_third = True

        self._credit_fielders_with_out(runner_name, fielders)
        self.double_play_flag = double_play

        if len(self.pitch_sequence) > 0:
            self.pitch_sequence = self.pitch_sequence[:-1] + constants.PITCH_CHARS.A_RUNNER_GOING_ON_THE_PITCH + self.pitch_sequence[-1]
        
        self._out(runner_name)
        if self.event_text == "K":
            self.event_text += "+"
            batting_event = True
        else:
            batting_event = False
        self.event_text += 'CS(' + ''.join([str(p) for p in fielders]) + ')'
        self.event_type = constants.EVENT_CODE.CAUGHT_STEALING
        if not batting_event:
            self._record_event(batting_event=False)

        self.pitch_sequence += constants.PITCH_CHARS.PLAY_NOT_INVOLVING_THE_BATTER

        #reset flags
        self.double_play_flag = False
        self.caught_stealing_for_runner_on_first = False
        self.caught_stealing_for_runner_on_second = False
        self.caught_stealing_for_runner_on_third = False

    def out_picked_off(self, runner_name, fielders):
        self._record_any_pending_runner_event()
        if runner_name == self.runner_on_first:
            self.pickoff_of_runner_on_first = True
        elif runner_name == self.runner_on_second:
            self.pickoff_of_runner_on_second = True
        elif runner_name == self.runner_on_third:
            self.pickoff_of_runner_on_third = True

        self._out(runner_name)
        self.event_text += 'PO(' + ''.join([str(p) for p in fielders]) + ')'
        self.event_type = constants.EVENT_CODE.PICKOFF
        self._record_event(batting_event=False)
        self.pitch_sequence += constants.PITCH_CHARS.PLAY_NOT_INVOLVING_THE_BATTER

        self.pickoff_of_runner_on_first = False
        self.pickoff_of_runner_on_second = False
        self.pickoff_of_runner_on_third = False

    def out_dropped_third_strike(self, fielders):
        self._record_any_pending_runner_event()
        self._out(self.batter)
        self.event_text += "K" + ''.join([str(f) for f in fielders])
        self.event_type = constants.EVENT_CODE.STRIKEOUT
        
    def out_fly_out(self, player_name, fielder_position, sacrifice=False):
        self._record_any_pending_runner_event()
        if self.batter != player_name:
            raise StandardError("{}\nFly out player {} who is not current batter {}".format(self.inning_string(), 
                                                                                        player_name, 
                                                                                        self.batter))
        self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        self.sacrifice_fly_flag = sacrifice
        fielder_position = self.lookup_position_num(fielder_position)
        self._credit_fielders_with_out(player_name, [fielder_position])
        self._out(self.batter)
        self.event_text += str(fielder_position) + "/F"
        self.event_type = constants.EVENT_CODE.GENERIC_OUT
        if sacrifice:
            self._batting_event_is_official = False
        # TODO: KEEP GOING ON THE EVENT_STRING

    def out_strike_out(self, player_name, swinging=False):
        self._record_any_pending_runner_event()
        """ strike out current batter, swinging is True or False (for looking)"""
        if self.batter != player_name:
            raise StandardError("{}\nStrike Out player {} who is not current batter {}".format(self.inning_string(),
                                                                                       player_name, 
                                                                                       self.batter))
        self._credit_fielders_with_out(player_name, [2])
        self._out(self.batter)
        logger.debug("Strike out for {outs} outs".format(outs=self.outs))
        self.event_text += "K"
        self.event_type = constants.EVENT_CODE.STRIKEOUT

    def out_unassisted(self, player_name, fielder_position, foul=False, double_play=False):
        self._record_any_pending_runner_event()
        if self.batter == player_name:
            self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        self._out(player_name)
        self.double_play_flag = double_play
        self.foul_flag = foul
        fielder_position = self.lookup_position_num(fielder_position)
        self._credit_fielders_with_out(player_name, [fielder_position])
        self.event_text += str(fielder_position)  #TODO: does unassisted have a modifier?
        self.event_type = constants.EVENT_CODE.GENERIC_OUT
        logger.debug("Unassisted out for {outs} outs".format(outs=self.outs))

    def out_popup(self, player_name, fielder_position, foul=False, sacrifice=False):
        self._record_any_pending_runner_event()
        if self.batter != player_name:
            raise StandardError("{}\nPopup Out player {} who is not current batter {}".format(self.inning_string(),
                                                                                          player_name,
                                                                                          self.batter))

        self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        self.foul_flag = foul
        self._out(self.batter)
        fielder_position = self.lookup_position_num(fielder_position)
        self._credit_fielders_with_out(player_name, [fielder_position])
        self.event_text += str(fielder_position) + "/P"
        self.event_type = constants.EVENT_CODE.GENERIC_OUT
        if sacrifice:
            self._batting_event_is_official = False
        logger.debug("Unassisted out for {outs} outs".format(outs=self.outs))

    #------------------------------------------------------------------------------
    # ADVANCE
    #------------------------------------------------------------------------------

    def hit_single(self, player_name, location=None):
        assert(player_name == self.batter)
        self._record_any_pending_runner_event()
        self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        if location is not None:
            self.hit_location = self.lookup_position_num(location)
        self.event_text += 'S' + str(self.hit_location)
        self.event_type = constants.EVENT_CODE.SINGLE
        self._advance_player(player_name, 1)
        self.hit_value = 1

    def hit_double(self, player_name, location=None):
        assert(player_name == self.batter)
        self._record_any_pending_runner_event()
        self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        if location is not None:
            self.hit_location = self.lookup_position_num(location)
        self.event_text += 'D' + str(self.hit_location)
        self.event_type = constants.EVENT_CODE.DOUBLE
        self._advance_player(player_name, 2)
        self.hit_value = 2

    def hit_triple(self, player_name, location=None):
        assert(player_name == self.batter)
        self._record_any_pending_runner_event()
        self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        if location is not None:
            self.hit_location = self.lookup_position_num(location)
        self.event_text += 'T' + str(self.hit_location)
        self.event_type = constants.EVENT_CODE.TRIPLE
        self._advance_player(player_name, 3)
        self.hit_value = 3

    def hit_home_run(self, player_name, location=None):
        assert(player_name == self.batter)
        self._record_any_pending_runner_event()
        self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        if location is not None:
            self.hit_location = self.lookup_position_num(location)
        self.event_text += 'HR' + str(self.hit_location)
        self.event_type = constants.EVENT_CODE.HOME_RUN
        self._advance_player(player_name, 4)
        self.hit_value = 4

    def advance_on_wild_pitch(self, player_name, base):
        self.wild_pitch_flag = True
        if self.event_text != "WP":
            self.event_text += "WP"
            self.pitch_sequence += constants.PITCH_CHARS.PLAY_NOT_INVOLVING_THE_BATTER
        self.event_type = constants.EVENT_CODE.WILD_PITCH
        self._advance_player(player_name, base)
        #self._record_event(batting_event = False)
        self._pending_runner_event = True

    def advance_on_passed_ball(self, player_name, base):
        self.passed_ball_flag = True
        if self.event_text != "PB":
            self.event_text += "PB"
            self.pitch_sequence += constants.PITCH_CHARS.PLAY_NOT_INVOLVING_THE_BATTER
        self.event_type = constants.EVENT_CODE.PASSED_BALL
        self._advance_player(player_name, base)
        #self._record_event(batting_event = False)
        self._pending_runner_event = True

    def advance_on_stolen_base(self, player_name, base):
        if player_name == self.runner_on_first:
            self.stolen_base_for_runner_on_first = True
        elif player_name == self.runner_on_second:
            self.stolen_base_for_runner_on_second = True
        elif player_name == self.runner_on_third:
            self.stolen_base_for_runner_on_third = True

        if len(self.pitch_sequence) > 0:
            self.pitch_sequence = self.pitch_sequence[:-1] + constants.PITCH_CHARS.A_RUNNER_GOING_ON_THE_PITCH + self.pitch_sequence[-1]
        if self.event_text != "SB":
            self.event_text += "SB" + str(constants.BASE_LOOKUP[base])
        self.event_type = constants.EVENT_CODE.STOLEN_BASE
        self._advance_player(player_name, base, earned=False)
        #self._record_event(batting_event=False)
        self._pending_runner_event = True

        self.pitch_sequence += constants.PITCH_CHARS.PLAY_NOT_INVOLVING_THE_BATTER

        # reset the stolen base flags now that event has been sent
        self.stolen_base_for_runner_on_first = False
        self.stolen_base_for_runner_on_second = False
        self.stolen_base_for_runner_on_third = False

    def advance_on_throw(self, player_name, base):
        self._record_any_pending_runner_event()
        self._advance_player(player_name, base)
        self.event_text += "TH"

    def advance_on_error(self, player_name, base, error_position, error_type):
        self._record_any_pending_runner_event()
        if self.batter == player_name:
            self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        self.error(error_position, error_type)
        self.event_text += 'E' + str(self.lookup_position_num(error_position))
        self.event_type = constants.EVENT_CODE.ERROR
        self._advance_player(player_name, base)

    def advance_on_fielders_choice(self, player_name, base):
        self._record_any_pending_runner_event()
        if self.batter == player_name:
            self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        self.event_text += 'FC'
        self.event_type = constants.EVENT_CODE.FIELDERS_CHOICE
        self._advance_player(player_name, base)

    def advance_on_ground_rule(self, player_name, base):
        """Ground Rule Double"""
        self._record_any_pending_runner_event()
        if self.batter == player_name:
            self.pitch_sequence += constants.PITCH_CHARS.BALL_PUT_INTO_PLAY_BY_BATTER
        self.event_text += 'DGR'
        self.event_type = constants.EVENT_CODE.DOUBLE
        self._advance_player(player_name, base)

    def advance_on_hit_by_pitch(self, player_name):
        self._record_any_pending_runner_event()
        self.pitch_sequence += constants.PITCH_CHARS.HIT_BATTER
        self.event_text += 'HP'
        self.event_type = constants.EVENT_CODE.HIT_BY_PITCH
        self._advance_player(player_name, 1)
        self._batting_event_is_official = False

    def advance_on_walk(self, player_name, intentional=False):
        self._record_any_pending_runner_event()
        self.pitch_sequence += constants.PITCH_CHARS.BALL
        if intentional:
            self.pitch_sequence.replace(constants.PITCH_CHARS.BALL, constants.PITCH_CHARS.INTENTIONAL_BALL)
            self.event_text += 'IW'
            self.event_type = constants.EVENT_CODE.INTENTIONAL_WALK
        else:
            self.event_text += 'W'
            self.event_type = constants.EVENT_CODE.WALK
        self._advance_player(player_name, 1)
        self._batting_event_is_official = False
        
    def advance_on_dropped_third_strike(self, player_name):
        assert(player_name == self.batter)
        self.pitch_sequence += constants.PITCH_CHARS.STRIKE_UNKNOWN_TYPE
        self.event_text += 'KPB'
        self.event_type = constants.EVENT_CODE.STRIKEOUT
        self._advance_player(player_name, 1)

    def advance_from_batter(self, player_name, base, batter_number):
        self._record_any_pending_runner_event()
        current_batter = self.batting_lineup.find_player_by_name(self.batter)
        if batter_number != current_batter.number:
            logger.warning("Advance recorded from batter number {} that is not current batter {}".format(batter_number, self.batter))
        self._advance_player(player_name, base)

    def advance_from_interference(self, player_name, position=None):
        if self.batter != player_name:
            raise StandardError("{}\nAdvance from Interference player {} who is not current batter {}".format(self.self.inning_string(),
                                                                                                          player_name, 
                                                                                                          self.batter))

        self._advance_player(player_name, 1)
        if position is not None:
            self.event_text += 'C/E' + str(self.lookup_position_num(position))
        else:
            self.event_text += 'C'
        self.event_type = constants.EVENT_CODE.INTERFERENCE
        self._batting_event_is_official = False

    def base_string(self):
        return "B: {}, 1: {}, 2: {}, 3: {}".format(self.batter,
                                                self.runner_on_first,
                                                self.runner_on_second,
                                                self.runner_on_third
                                                )

    def _advance_player(self, player_name, base, earned=True):
        """
        advance runners to a base
        
        earned applies only to advances to home
        
        TODO: break this into 3 specific methods to advance a runner to a specific base
        This will make it easier to use this method with whatever parsing means we need
        """
        base_num = constants.BASE_LOOKUP[base]
        logger.info("%s to %s" % (player_name, base_num))

        
        if base_num == 4 and not earned:
            destination_base_name = 5
            #TODO: add special case of earned by pitcher unearned by batting team = 6
        else:
            destination_base_name = base_num

        if self.batter == player_name:
            self.batter_destination = destination_base_name
        elif player_name == self.runner_on_first:
            self.runner_on_first_destination = destination_base_name
        elif player_name == self.runner_on_second:
            self.runner_on_second_destination = destination_base_name
        elif player_name == self.runner_on_third:
            self.runner_on_third_destination = destination_base_name

        #TODO: confirm we want to use the result_pitcher here with the pitcher charged
        advance_string = self._bases.advance(player_name, base_num)
        if advance_string.startswith("B"):
            if self.batter != player_name:
                logger.warning("Player {} neither batter nor found on bases for advance to {}".format(player_name, base))
                raise StandardError("Lost Player")
        self._advancing_event_text += '.' + advance_string

        if base_num == 1:
            self._pending_pitcher_charged_with_runner_on_first = self.result_pitcher
        elif base_num == 2:
            self._pending_pitcher_charged_with_runner_on_second = self.result_pitcher
        elif base_num == 3:
            self._pending_pitcher_charged_with_runner_on_second = self.result_pitcher
        elif base_num == 4:
            self._score(earned)
        #logger.debug("runners now 1st %s, 2nd %s, 3rd, %s" % (self.runner_on_first, self.runner_on_second, self.runner_on_third))
        if self.batter == player_name:
            self._increment_batting_order()

    def _score(self, earned):
        self.runs_scored_in_this_half_inning += 1
        if earned:
            self.rbi_on_play += 1  #TODO: do rbi's count on unearned?
        if self.bat_home_id:
            self.home_score += 1
        else:
            self.visitor_score += 1
        logger.debug("Score now Home %s, Vis %s" % (self.home_score, self.visitor_score))

    #------------------------------------------------------------------------------
    # SUBSTITUTIONS
    #------------------------------------------------------------------------------

    def defensive_sub(self, new_player_name, replacing_name, position=''):
        # "moves to" or "subs at" Case
        logging.info("DEFENSIVE SUB -- {} for {} at {}".format(new_player_name, replacing_name, position))
        if replacing_name == '':
            if position == '':
                raise StandardError("Defensive Sub Error, no new position or replacement name")
            current_defense = self._current_fielding_lineup()
            try:
                # player moves to new position
                current_defense.find_player_by_name(new_player_name)
                current_defense.set_player_position(new_player_name, position)
                logging.info("{} moves to {}".format(new_player_name, position))
            except KeyError:
                # player substitutes
                new_player = self._current_fielding_roster().find_player_by_name(new_player_name)
                new_player.set_position(position)
                removed_player = current_defense.find_player_by_position(position)
                new_player.order = removed_player.order
                current_defense.remove_player(removed_player.name)
                current_defense.add_player(new_player)
        else:
            possible_remove_player = self._current_fielding_lineup().find_player_by_name(replacing_name)
            if possible_remove_player.position == position:
                removed_player = self._current_fielding_lineup().remove_player(replacing_name)
                new_player = self._current_fielding_roster().find_player_by_name(new_player_name)
                if position != '':
                    new_player.set_position(position)
                new_player.order = removed_player.order
            else:  # the player being replaced is not in the position anymore
                # this should only apply to taking a pitchers spot...
                new_player = self._current_fielding_roster().find_player_by_name(new_player_name)
                if position != '':
                    new_player.set_position(position)
                new_player.order = possible_remove_player.order
                #assert (possible_remove_player.position == 'P')
                #possible_remove_player.order = None
            try:
                self._current_fielding_lineup().add_player(new_player)
            except LineupError:
                existing_player = self._current_fielding_roster().find_player_by_name(new_player.name)
                existing_player.merge(new_player)
                logger.warn("{} already in lineup.  diffs => {}".format(new_player.name, existing_player.diff(new_player)))
        

        self._update_position_attributes_with_player( self._current_fielding_roster().find_player_by_name(new_player_name))

    def _update_position_attributes_with_player(self, new_player, responsible_pitcher = True):
        """
        Update the position attributes for this new player
        
        #WARN: this will update the pitcher and result_pitcher as well.
        # at this time, the college scoring system does not appear to indicate mid-play 
        # substitutions that I can detect
        """
        if new_player.position == 'P':
            self.pitcher = new_player.name
            self.pitcher_hand = new_player.hand
            if responsible_pitcher:
                self.result_pitcher = new_player.name 
                self.result_pitcher_hand = self.pitcher_hand
        elif new_player.position == 'C':
            self.catcher = new_player.name
        elif new_player.position == '1B':
            self.first_baseman = new_player.name
        elif new_player.position == '2B':
            self.second_baseman = new_player.name
        elif new_player.position == '3B':
            self.third_baseman = new_player.name
        elif new_player.position == 'SS':
            self.shortstop = new_player.name
        elif new_player.position == 'LF':
            self.left_fielder = new_player.name
        elif new_player.position == 'CF':
            self.center_fielder = new_player.name
        elif new_player.position == 'RF':
            self.right_fielder = new_player.name        
        

    def offensive_sub(self, new_player_name, replacing_name, pinch_runner=False, base=None):
        removed_player = self._current_batting_lineup().remove_player(replacing_name)
        new_player = self._current_batting_roster().find_player_by_name(new_player_name)
        self._current_batting_lineup().add_player(new_player)

        if pinch_runner:
            logging.info("OFFENSIVE SUB -- {} running for {} at {}".format(new_player_name, replacing_name, base))

            base_num = constants.BASE_LOOKUP[base]
            # 1. assert that we are replacing the right guy
            # 2. set the pinch runner flag to true (I checked MLB data, and this flag is True only for
            # the first event after the offensive substitution - TDH)
            # 3. put the new runner on base
            self._bases.replace_runner(new_player_name, removed_player.name, base_num)
            if base_num == 1:
                assert(self.runner_on_first == removed_player.name)
                self.pinch_runner_on_first = True
                self.runner_on_first = new_player.name
                self.runner_removed_for_pinch_runner_on_first = removed_player.name
            elif base_num == 2:
                assert(self.runner_on_second == removed_player.name)
                self.pinch_runner_on_second = True
                self.runner_on_second = new_player.name
                self.runner_removed_for_pinch_runner_on_second = removed_player.name
            elif base_num == 3:
                assert(self.runner_on_third == removed_player.name)
                self.pinch_runner_on_third = True
                self.runner_on_third = new_player.name
                self.runner_removed_for_pinch_runner_on_third = removed_player.name

        else:
            logging.info("offensive sub -- {} hitting for {}".format(new_player_name, replacing_name))
            self._next_batter_pinch = True

        new_player.position = None  #TODO: make sure these guys get a position before they field
        new_player.order = removed_player.order
