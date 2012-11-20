"""
GameState is a python class to represent the ongoing gamestate
as parsed by a play by play parser.  The attributes of this class
have a one-to-one relationship with the Chadwick Event Descriptor.

Therefore, at any time, this class may be added as a line in a SQL event database
"""

import logging
import pprint
logger = logging.getLogger("gamestate")
import constants

from models import event
import eventfields

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
        self.result_batter = None
        self.result_batter_hand = None
        
        self.pitcher = None
        self.pitcher_hand = None
        self.result_pitcher = None
        self.result_pitcher_hand = None
        
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
        
        self.event_text = None
        self.leadoff_flag = False
        self.pinch_hit_flag = False
        self.defensive_position = None
        self.lineup_position = None
        
        #TODO
        self.event_type = None
        self.batter_event_flag = False
        self.official_time_at_bat_flag = False
        self.hit_value = None
        self.sacrifice_hit_flag = False
        self.sacrifice_fly_flag = False
        self.outs_on_play = 0
        self.double_play_flag = False
        self.triple_play_flag = False
        self.rbi_on_play = None
        self.wild_pitch_flag = False
        self.passed_ball_flag = False
        self.fielded_by = None
        self.batted_ball_type = None
        self.bunt_flag = False
        self.foul_flag = False
        self.hit_location = None
        self.number_of_errors = None
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
        self.stolen_base_for_runner_on_first = None
        self.stolen_base_for_runner_on_second = None
        self.stolen_base_for_runner_on_third = None
        self.caught_stealing_for_runner_on_first = None
        self.caught_stealing_for_runner_on_second = None
        self.caught_stealing_for_runner_on_third = None
        self.pickoff_of_runner_on_first = None
        self.pickoff_of_runner_on_second = None
        self.pickoff_of_runner_on_third = None
        self.pitcher_charged_with_runner_on_first = None
        self.pitcher_charged_with_runner_on_second = None
        self.pitcher_charged_with_runner_on_third = None
        self.new_game_flag = False
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
        self.event_number = None

        # Extended Fields
        self.description = None
        self.home_team_id = None
        self.batting_team_id = None
        self.fielding_team_id = None
        self.half_inning = None # (differs_from_batting_team_if_home_team_bats_first)
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
        
        # Non Model attributes:
        self._next_batter_pinch = False
        self._next_batter_leadoff = False
        
    def set_home_lineup(self, lineup):
        """
        set with Lineup object
        """
        self.home_lineup = lineup 
        
    def set_away_lineup(self, lineup):
        """
        set with Lineup object
        """
        self.away_lineup = lineup
    
    def _swap_lineups(self, bat_home=True):
        """
        set with a list of players in numbered positioin order
        """
        if bat_home:
            self.batting_lineup = self.home_lineup
            self.fielding_lineup = self.away_lineup
        else:
            self.batting_lineup = self.away_lineup
            self.fielding_lineup = self.home_lineup
            
        fielder_pos_dict = self.fielding_lineup.position_dict()
        
        self.pitcher = fielder_pos_dict["P"]
        self.catcher = fielder_pos_dict["C"]
        self.first_baseman = fielder_pos_dict["1B"]
        self.second_baseman = fielder_pos_dict["2B"]
        self.third_baseman  = fielder_pos_dict["3B"]
        self.shortstop = fielder_pos_dict["SS"]
        self.left_fielder = fielder_pos_dict["LF"]
        self.center_fielder = fielder_pos_dict["CF"]
        self.right_fielder = fielder_pos_dict["RF"]
            
    def copy_to_event_model(self):
        newmodel = event.Event()
        for key, modelattribute in MODEL_LOOKUP_DICT.items():
            newmodel.__dict__[modelattribute] = self.__dict__[key]
        return newmodel

    def new_batter(self, batter):
        self.batter = batter
        self.balls = 0
        self.strikes = 0
        self.outs_on_play = 0
        self.pitch_sequence = ''
        self.event_text = ''
        
        if self.bat_home_id:
            current_lineup = self.home_lineup
        else:
            current_lineup = self.away_lineup
        try:
            player = current_lineup.find_player_by_name(self.batter)
            self.defensive_position = player.position
            self.lineup_position = player.order
            
        except KeyError, e:
            logger.error(str(e) + "\n %s not found in lineup \n%s" % (self.batter, str(current_lineup)))
            raise
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
        
        logger.debug("new batter %s" % batter)

    def new_inning(self):
        self.inning += 1
        self.new_half()
        
    def new_half(self):
        self.outs = 0
        self.runner_on_first = None
        self.runner_on_second = None
        self.runner_on_third = None
        
        if self.inning != 0:
            self.half_inning = int(not self.half_inning)
            self.bat_home_id = int(not self.bat_home_id)
            if self.half_inning == constants.TOP:
                self.inning += 1
        else:
            self.inning = 1
        self._swap_lineups(self.bat_home_id)        
        self._next_batter_leadoff = True
        logger.debug("new half: inning %s, %s" % (self.inning, self.get_half_string()))
            
    def get_half_string(self):
        if self.half_inning:
            return "Bottom"
        else:
            return "Top"

    def add_ball(self):
        self.balls += 1
        self.pitch_sequence += constants.BALL
        logger.debug("Ball")
        
    def add_called_strike(self):
        self.strikes += 1
        self.pitch_sequence += constants.CALLED_STRIKE
        logger.debug("Called Strike")

    def add_swinging_strike(self):
        self.strikes += 1
        self.pitch_sequence += constants.SWINGING_STRIKE
        logger.debug("Swinging Strike")

    def add_foul(self):
        if self.strikes < 2:
            self.strikes += 1
        self.pitch_sequence += constants.FOUL
        logger.debug("Foul")

    def add_pickoff(self, a, b, c):
        pass
        # TODO: write pick off method

    def add_out(self):
        self.outs += 1
        self.outs_on_play += 1
        logger.debug("Out %s" % self.outs)
        
    def add_score(self):
        self.runs_scored_in_this_half_inning += 1
        if self.bat_home_id:
            self.home_score += 1
        else:
            self.visitor_score += 1
        logger.debug("Score now Home %s, Vis %s" % (self.home_score, self.visitor_score))
            
    def add_advance(self, text, location, tokens):
        """
        advance runners to a base
        
        TODO: break this into 3 specific methods to advance a runner to a specific base
        This will make it easier to use this method with whatever parsing means we need
        """
        tdict = tokens.asDict()
        player = ' '.join(tdict["player"][1:])
        base = tdict["base"][0]
        logger.info("%s to %s" % ( player, base))
        if base == '1st':
            self.runner_on_first = player 
        elif base == '2nd':
            if self.runner_on_first == player:
                self.runner_on_first = None
            self.runner_on_second = player
        elif base == '3rd':
            if self.runner_on_first == player:
                self.runner_on_first = None
            if self.runner_on_second == player:
                self.runner_on_second = None
            self.runner_on_third = player
        logger.info("runners now 1st %s, 2nd %s, 3rd, %s" % (self.runner_on_first, self.runner_on_second, self.runner_on_third))
        
    def add_out_description(self, text, location, tokens):
        self.event_text = text #TODO: - not correct
        
    def fielder_substitution(self, text, location, tokens):
        pass #print tokens.asDict()

    def offensive_substitution(self, text, location, tokens):
        self._next_batter_pinch = True
        newplayer = tokens[constants.PARSING.NEW_PLAYER]
        replacing = tokens[constants.PARSING.REPLACING]

                
        logger.error(pprint.pformat(tokens.asDict()))
        
        
        pass #print tokens.asDict()
        