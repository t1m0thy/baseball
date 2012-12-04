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
        
        self.event_text = None  #TODO: implement event_text
        self.leadoff_flag = False
        self.pinch_hit_flag = False
        self.defensive_position = None
        self.lineup_position = None

        self.event_type = None #TODO: implement event_type
        
        self.batter_event_flag = False # True in near all cases except recording stolen bases or caught stealing events
        self.official_time_at_bat_flag = False # True unless there was a running event 
        self.hit_value = 0 
        
        self.sacrifice_hit_flag = False
        self.sacrifice_fly_flag = False
        self.outs_on_play = 0
        self.double_play_flag = False
        self.triple_play_flag = False
        self.rbi_on_play = 0
        self.wild_pitch_flag = False
        self.passed_ball_flag = False
        
        self.fielded_by = None
        self.batted_ball_type = None
        self.bunt_flag = False
        self.foul_flag = False
        self.hit_location = None
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
        self._home_place_in_batting_order = 1  #always start with leadoff batter
        self._away_place_in_batting_order = 1  #always start with leadoff batter
        self.current_order = 1
        self._last_batter = None

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
    # UTILITIES
    #------------------------------------------------------------------------------ 

    def export_runner_event(self):
        """ 
        in the case of runner events, send new record to database 
        ie.  stolen base, caught stealing, balk, pickoff, out advancing, 
        wild pitch, passed ball
        """
        pass
           
    def _swap_lineups(self, bat_home=True):
        """
        set with a list of players in numbered positioin order
        """
        if bat_home:
            self.batting_lineup = self.home_lineup
            self.fielding_lineup = self.away_lineup
            self.current_order = self._home_place_in_batting_order
        else:
            self.batting_lineup = self.away_lineup
            self.fielding_lineup = self.home_lineup
            self.current_order = self._away_place_in_batting_order
            
        fielder_pos_dict = self.fielding_lineup.position_dict()
        self.pitcher = fielder_pos_dict['P']
        self.catcher = fielder_pos_dict['C']
        self.first_baseman = fielder_pos_dict['1B']
        self.second_baseman = fielder_pos_dict['2B']
        self.third_baseman  = fielder_pos_dict['3B']
        self.shortstop = fielder_pos_dict['SS']
        self.left_fielder = fielder_pos_dict['LF']
        self.center_fielder = fielder_pos_dict['CF']
        self.right_fielder = fielder_pos_dict['RF']
            
    def copy_to_event_model(self):
        newmodel = event.Event()
        for key, modelattribute in MODEL_LOOKUP_DICT.items():
            newmodel.__dict__[modelattribute] = self.__dict__[key]
        return newmodel

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
                self.current_order = self._home_place_in_batting_order
            else:
                self._away_place_in_batting_order += 1
                if self._away_place_in_batting_order > 9:
                    self._away_place_in_batting_order = 1
                self.current_order = self._away_place_in_batting_order
            # increment the atbat count
            self._current_batting_lineup().find_player_by_name(self.batter).atbats += 1

    def get_half_string(self):
        if self.half_inning:
            return "Bottom"
        else:
            return "Top"
       
    #------------------------------------------------------------------------------ 
    #  NEW CALLS
    #------------------------------------------------------------------------------ 
    def new_batter(self, batter):
        self.batter = batter
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
        logger.info("-> %s to bat" % batter)

        # If this the first batter in a new half, swap the lineups
        # we wait to perform this swap in order to allow any defensive substitutions to be swapped at the beginning of the half
        if self._next_batter_leadoff:
            self._swap_lineups(self.bat_home_id)        

        try:
            batter_player = self._current_batting_lineup().find_player_by_name(self.batter)
            assert(batter_player.order == self.current_order)
            #print "%s order %s matches %s" % (batter_player.name, batter_player.order, current_order)
            self.defensive_position = batter_player.position
            self.lineup_position = batter_player.order            
        except KeyError, e:
            # Player not in lineup
            logger.warning(self.batter + " not found in lineup for atbat")
            try:
                new_player = self._current_batting_roster().find_player_by_name(self.batter)
                replacing_player = self._current_batting_lineup().find_player_by_order(self.current_order)
                logger.warning("Used roster for auto-substitution of %s for %s" % (new_player.name, replacing_player.name))
                self.offensive_sub(new_player.name, replacing_player.name)
                # normally in an offensive sub, the player position would be PH
                # in the case of an auto sub, we are going to just that player the position of the old player
                # this is because there likely wont be a defensive sub either to put this new player in the correct position 
                new_player.position = replacing_player.position
                self.defensive_position = new_player.position
                self.lineup_position = new_player.order 
            except KeyError:
                raise StandardError("Auto Replace Failed.  %s not found in roster" % self.batter)
        except AssertionError, e:
            # Player order doesn't match expected order
            logger.warning("%s %s doesn't match expected order %s" % (batter_player.name, batter_player.order, self.current_order))
            if batter_player.atbats == 0:
                swap_with_player = self._current_batting_lineup().find_player_by_order(self.current_order)
                if swap_with_player.atbats == 0:
                    swap_with_player.order = batter_player.order
                    batter_player.order = self.current_order
                    logger.warning("Used roster for auto-order swap of %s for %s" % (batter_player.name, swap_with_player.name))
                else:
                    raise                
            else:
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
        self._next_batter_leadoff = True
        #NOTE: lineups will be swapped when the first batter is called.
        # this allows any initial defensive subs to be performed prior to the first batter 
        
        logger.info("--------- {half} of the {inning}".format(inning=self.inning, half=self.get_half_string()))

    #------------------------------------------------------------------------------ 
    #  PITCHES
    #------------------------------------------------------------------------------ 

    def pitch_ball(self):
        self.balls += 1
        self.pitch_sequence += constants.BALL
        logger.debug("Ball")
        
    def pitch_called_strike(self):
        self.strikes += 1
        self.pitch_sequence += constants.CALLED_STRIKE
        logger.debug("Called Strike")

    def pitch_swinging_strike(self):
        self.strikes += 1
        self.pitch_sequence += constants.SWINGING_STRIKE
        logger.debug("Swinging Strike")

    def pitch_foul(self):
        if self.strikes < 2:
            self.strikes += 1
        self.pitch_sequence += constants.FOUL
        logger.debug("Foul")
        
    def pitch_pickoff_attempt(self, base, thrower_position, catcher_position):
        """
        record a pickoff attempt by pitcher
        
        args:
        base: 1, 2, or 3: the base where PO throw went
        """
        logger.debug("Pickoff at {}, {} to {}".format(base, thrower_position, catcher_position))
        base_num = constants.BASE_LOOKUP[base]
        if base_num not in [1,2,3]:
            raise StandardError("pickoff base not a valid argument (1, 2, or 3)")  
        self.pitch_sequence += base
        
    #------------------------------------------------------------------------------ 
    # OUTS
    #------------------------------------------------------------------------------ 

    def _out(self, player_name):
        self.outs += 1
        self.outs_on_play += 1
        if player_name == self.batter:
            self._increment_batting_order()
        if self.outs > 3:
            raise StandardError("Recorded over 3 outs")
        
    def out_thrown_out(self, player_name, fielders, sacrifice = False, double_play = False, triple_play=False, unassisted=False):
        """ throw out a player 
        
        player_name - name of the player put out
        fielders - the string of the position players who did it. ie. "3U" "64" "543"
        """
        self.sacrifice_hit_flag = sacrifice
        self.double_play_flag = double_play
        self.triple_play_flag = triple_play
        logger.info("Fielders {}".format(fielders))
        self._out(player_name)
        
    def out_caught_stealing(self, runner_name, fielders):
        self._out(runner_name)

    def out_picked_off(self, runner_name, fielders):
        self._out(runner_name)

    def out_dropped_third_strike(self, fielders):
        self._out(self.batter)
        
    def out_fly_out(self, player_name, fielding_position, sacrifice=False):
        assert(player_name == self.batter)
        self.sacrifice_fly_flag = sacrifice
        self._out(self.batter)
         
    def out_strike_out(self, player_name, swinging=False):
        """ strike out current batter, swinging is True or False (for looking)"""
        assert(player_name == self.batter)
        self._out(self.batter)
        logger.debug("Strike out for {outs} outs".format(outs=self.outs))

    def out_unassisted(self, player_name, fielder_position, foul=False, double_play = False):
        self._out(player_name)
        self.double_play_flag = double_play
        logger.debug("Unassisted out for {outs} outs".format(outs=self.outs))
        
    def out_popup(self, player_name, fielder_position, foul=False, sacrifice=False):
        assert(player_name == self.batter)
        self._out(self.batter)
        logger.debug("Unassisted out for {outs} outs".format(outs=self.outs))

    #------------------------------------------------------------------------------ 
    # SCORE
    #------------------------------------------------------------------------------ 
        
    def add_score(self, player_name):
        self.runs_scored_in_this_half_inning += 1
        self.rbi_on_play += 1
        if self.bat_home_id:
            self.home_score += 1
        else:
            self.visitor_score += 1
        logger.debug("Score now Home %s, Vis %s" % (self.home_score, self.visitor_score))
        if player_name == self.batter:
            self._increment_batting_order()
            self.hit_value = 4

    #------------------------------------------------------------------------------ 
    # ADVANCE
    #------------------------------------------------------------------------------ 

    def advance_on_wild_pitch(self, player_name, base):
        self.wild_pitch_flag = True
        self._advance_player(player_name, base)
    
    def advance_on_passed_ball(self,  player_name, base):
        self.passed_ball_flag = True
        self._advance_player(player_name, base)
    
    
    def _advance_player(self, player_name, base):
        """
        advance runners to a base
        
        TODO: break this into 3 specific methods to advance a runner to a specific base
        This will make it easier to use this method with whatever parsing means we need
        """
        base_num = constants.BASE_LOOKUP[base]
        logger.info("%s to %s" % ( player_name, base))
        if base == 1:
            self.runner_on_first = player_name 
        elif base == 2:
            if self.runner_on_first == player_name:
                self.runner_on_first = None
            self.runner_on_second = player_name
        elif base == 3:
            if self.runner_on_first == player_name:
                self.runner_on_first = None
            if self.runner_on_second == player_name:
                self.runner_on_second = None
            self.runner_on_third = player_name
        #logger.debug("runners now 1st %s, 2nd %s, 3rd, %s" % (self.runner_on_first, self.runner_on_second, self.runner_on_third))
        if player_name == self.batter:
            self._increment_batting_order()  
            self.hit_value = base_num

    def defensive_sub(self, new_player_name, replacing_name, position=''):
        # "moves to" or "subs at" Case
        logging.info("DEFENSIVE SUB" + new_player_name + replacing_name + position)
        if replacing_name == '':
            if position == '':
                raise StandardError("Defensive Sub Error, no new position or replacement name")
            current_defense = self._current_fielding_lineup()
            try:
                # moves to case
                current_defense.find_player_by_name(new_player_name)
                current_defense.set_player_position(new_player_name, position)
                logging.info("{} moves to {}".format(new_player_name, position))
            except KeyError:
                # subs at case
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
            else: # the player being replaced is not in the position anymore
                # this should only apply to taking a pitchers spot...
                new_player = self._current_fielding_roster().find_player_by_name(new_player_name)
                if position != '':
                    new_player.set_position(position)
                new_player.order = possible_remove_player.order
                #assert (possible_remove_player.position == 'P')
                #possible_remove_player.order = None
            self._current_fielding_lineup().add_player(new_player)
                
    def offensive_sub(self, new_player_name, replacing_name):
        #TODO: this may not always be true
        self._next_batter_pinch = True
        removed_player = self._current_batting_lineup().remove_player(replacing_name)
        new_player = self._current_batting_roster().find_player_by_name(new_player_name)

        new_player.position =  None  #TODO: make sure these guys get a position before they field 
        
        new_player.order = removed_player.order  
        self._current_batting_lineup().add_player(new_player)
