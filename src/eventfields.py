"""
Lists of tuples showing ('Field number', 'Description', 'Header')

This list originated from the event descriptor of the chadwick open source project
http://chadwick.sourceforge.net/doc/cwevent.html

Descriptions (not header names) are modified so they may be codified into python attribute names
all hyphens are replaced with spaces: "pinch-hitter" becomes "pinch hitter"
and descriptions starting with numbers are replaced by words: "1st" becomes "first"

This way, all descriptions can be converted to attribute names
by replacing spaces with underscores
and making all characters lowercase
any paranthetical comments from description are converted to comments here

see utility functions at bottom of file

NOTES:
the above chadwich side says hit value is H_FL.
This has been changed to H_CD to match MLB example database.

"""
cw_event_fields = [('0', 'Game ID', 'GAME_ID'),
 ('1', 'Visiting team', 'AWAY_TEAM_ID'),
 ('2', 'Inning', 'INN_CT'),
 ('3', 'Bat Home id', 'BAT_HOME_ID'),  # TDH - Description altered to match easier attribute
 ('4', 'Outs', 'OUTS_CT'),
 ('5', 'Balls', 'BALLS_CT'),
 ('6', 'Strikes', 'STRIKES_CT'),
 ('7', 'Pitch sequence', 'PITCH_SEQ_TX'),
 ('8', 'Visitor score', 'AWAY_SCORE_CT'),
 ('9', 'Home score', 'HOME_SCORE_CT'),
 ('10', 'Batter', 'BAT_ID'),
 ('11', 'Batter hand', 'BAT_HAND_CD'),
 ('12', 'Result batter', 'RESP_BAT_ID'),
 ('13', 'Result batter hand', 'RESP_BAT_HAND_CD'),
 ('14', 'Pitcher', 'PIT_ID'),
 ('15', 'Pitcher hand', 'PIT_HAND_CD'),
 ('16', 'Result pitcher', 'RES_PIT_ID'),  #This was changed from RESP_PIT_ID (from docs) to match MLB example
 ('17', 'Result pitcher hand', 'RES_PIT_HAND_CD'), #This was changed from RESP_PIT_HAND_CD (from docs) to match MLB example
 ('18', 'Catcher', 'POS2_FLD_ID'),
 ('19', 'First baseman', 'POS3_FLD_ID'),
 ('20', 'Second baseman', 'POS4_FLD_ID'),
 ('21', 'Third baseman', 'POS5_FLD_ID'),
 ('22', 'Shortstop', 'POS6_FLD_ID'),
 ('23', 'Left fielder', 'POS7_FLD_ID'),
 ('24', 'Center fielder', 'POS8_FLD_ID'),
 ('25', 'Right fielder', 'POS9_FLD_ID'),
 ('26', 'Runner on first', 'BASE1_RUN_ID'),
 ('27', 'Runner on second', 'BASE2_RUN_ID'),
 ('28', 'Runner on third', 'BASE3_RUN_ID'),
 ('29', 'Event text', 'EVENT_TX'),
 ('30', 'Leadoff flag', 'LEADOFF_FL'),
 ('31', 'Pinch hit flag', 'PH_FL'),
 ('32', 'Defensive position', 'BAT_FLD_CD'),
 ('33', 'Lineup position', 'BAT_LINEUP_ID'),
 ('34', 'Event type', 'EVENT_CD'),
 ('35', 'Batter event flag', 'BAT_EVENT_FL'),
 ('36', 'Official time at bat flag', 'AB_FL'),
 ('37', 'Hit value', 'H_CD'),  #This was changed from H_FL (from docs) to match MLB example
 ('38', 'Sacrifice hit flag', 'SH_FL'),
 ('39', 'Sacrifice fly flag', 'SF_FL'),
 ('40', 'Outs on play', 'EVENT_OUTS_CT'),
 ('41', 'Double play flag', 'DP_FL'),
 ('42', 'Triple play flag', 'TP_FL'),
 ('43', 'RBI on play', 'RBI_CT'),
 ('44', 'Wild pitch flag', 'WP_FL'),
 ('45', 'Passed ball flag', 'PB_FL'),
 ('46', 'Fielded by', 'FLD_CD'),
 ('47', 'Batted ball type', 'BATTEDBALL_CD'),
 ('48', 'Bunt flag', 'BUNT_FL'),
 ('49', 'Foul flag', 'FOUL_FL'),
 ('50', 'Hit location', 'BATTEDBALL_LOC_TX'),
 ('51', 'Number of errors', 'ERR_CT'),
 ('52', 'First error player', 'ERR1_FLD_CD'),
 ('53', 'First error type', 'ERR1_CD'),
 ('54', 'Second error player', 'ERR2_FLD_CD'),
 ('55', 'Second error type', 'ERR2_CD'),
 ('56', 'Third error player', 'ERR3_FLD_CD'),
 ('57', 'Third error type', 'ERR3_CD'),
 ('58', 'Batter destination', 'BAT_DEST_ID'),
 ('59', 'Runner on first destination', 'RUN1_DEST_ID'),
 ('60', 'Runner on second destination', 'RUN2_DEST_ID'),
 ('61', 'Runner on third destination', 'RUN3_DEST_ID'),
 ('62', 'Play on batter', 'BAT_PLAY_TX'),
 ('63', 'Play on runner on first', 'RUN1_PLAY_TX'),
 ('64', 'Play on runner on second', 'RUN2_PLAY_TX'),
 ('65', 'Play on runner on third', 'RUN3_PLAY_TX'),
 ('66', 'Stolen base for runner on first', 'RUN1_SB_FL'),
 ('67', 'Stolen base for runner on second', 'RUN2_SB_FL'),
 ('68', 'Stolen base for runner on third', 'RUN3_SB_FL'),
 ('69', 'Caught stealing for runner on first', 'RUN1_CS_FL'),
 ('70', 'Caught stealing for runner on second', 'RUN2_CS_FL'),
 ('71', 'Caught stealing for runner on third', 'RUN3_CS_FL'),
 ('72', 'Pickoff of runner on first', 'RUN1_PK_FL'),
 ('73', 'Pickoff of runner on second', 'RUN2_PK_FL'),
 ('74', 'Pickoff of runner on third', 'RUN3_PK_FL'),
 ('75', 'Pitcher charged with runner on first', 'RUN1_RESP_PIT_ID'),
 ('76', 'Pitcher charged with runner on second', 'RUN2_RESP_PIT_ID'),
 ('77', 'Pitcher charged with runner on third', 'RUN3_RESP_PIT_ID'),
 ('78', 'New game flag', 'GAME_NEW_FL'),
 ('79', 'End game flag', 'GAME_END_FL'),
 ('80', 'Pinch runner on first', 'PR_RUN1_FL'),
 ('81', 'Pinch runner on second', 'PR_RUN2_FL'),
 ('82', 'Pinch runner on third', 'PR_RUN3_FL'),
 ('83', 'Runner removed for pinch runner on first', 'REMOVED_FOR_PR_RUN1_ID'),
 ('84', 'Runner removed for pinch runner on second', 'REMOVED_FOR_PR_RUN2_ID'),
 ('85', 'Runner removed for pinch runner on third', 'REMOVED_FOR_PR_RUN3_ID'),
 ('86', 'Batter removed for pinch hitter', 'REMOVED_FOR_PH_BAT_ID'),
 ('87', 'Position of batter removed for pinch hitter', 'REMOVED_FOR_PH_BAT_FLD_CD'),
 ('88', 'Fielder with first putout', 'PO1_FLD_CD'),
 ('89', 'Fielder with second putout', 'PO2_FLD_CD'),
 ('90', 'Fielder with third putout', 'PO3_FLD_CD'),
 ('91', 'Fielder with first assist', 'ASS1_FLD_CD'),
 ('92', 'Fielder with second assist', 'ASS2_FLD_CD'),
 ('93', 'Fielder with third assist', 'ASS3_FLD_CD'),
 ('94', 'Fielder with fourth assist', 'ASS4_FLD_CD'),
 ('95', 'Fielder with fifth assist', 'ASS5_FLD_CD'),
 ('96', 'Event number', 'EVENT_ID')]

cw_event_fields_extended = [
 ('Field number', 'Description', 'Header'),
 ('0', 'home team id', 'HOME_TEAM_ID'),
 ('1', 'batting team id', 'BAT_TEAM_ID'),
 ('2', 'fielding team id', 'FLD_TEAM_ID'),
 ('3', 'half inning', 'BAT_LAST_ID'),  # (differs from batting team if home team bats first)
 ('4', 'start of half inning flag', 'INN_NEW_FL'),
 ('5', 'end of half inning flag', 'INN_END_FL'),
 ('6', 'score for team on offense', 'START_BAT_SCORE_CT'),
 ('7', 'score for team on defense', 'START_FLD_SCORE_CT'),
 ('8', 'runs scored in this half inning', 'INN_RUNS_CT'),
 ('9', 'number of plate appearances in game for team on offense', 'GAME_PA_CT'),
 ('10', 'number of plate appearances in inning for team on offense', 'INN_PA_CT'),
 ('11', 'start of plate appearance flag', 'PA_NEW_FL'),
 ('12', 'truncated plate appearance flag', 'PA_TRUNC_FL'),
 ('13', 'base state at start of play', 'START_BASES_CD'),
 ('14', 'base state at end of play', 'END_BASES_CD'),
 ('15', 'batter is starter flag', 'BAT_START_FL'),
 ('16', 'result batter is starter flag', 'RESP_BAT_START_FL'),
 ('17', 'ID of the batter on deck', 'BAT_ON_DECK_ID'),
 ('18', 'ID of the batter in the hold', 'BAT_IN_HOLD_ID'),
 ('19', 'pitcher is starter flag', 'PIT_START_FL'),
 ('20', 'result pitcher is starter flag', 'RESP_PIT_START_FL'),
 ('21', 'defensive position of runner on first', 'RUN1_FLD_CD'),
 ('22', 'lineup position of runner on first', 'RUN1_LINEUP_CD'),
 ('23', 'event number on which runner on first reached base', 'RUN1_ORIGIN_EVENT_ID'),
 ('24', 'defensive position of runner on second', 'RUN2_FLD_CD'),
 ('25', 'lineup position of runner on second', 'RUN2_LINEUP_CD'),
 ('26', 'event number on which runner on second reached base', 'RUN2_ORIGIN_EVENT_ID'),
 ('27', 'defensive position of runner on third', 'RUN3_FLD_CD'),
 ('28', 'lineup position of runner on third', 'RUN3_LINEUP_CD'),
 ('29', 'event number on which runner on third reached base', 'RUN3_ORIGIN_EVENT_ID'),
 ('30', 'responsible catcher for runner on first', 'RUN1_RESP_CAT_ID'),
 ('31', 'responsible catcher for runner on second', 'RUN2_RESP_CAT_ID'),
 ('32', 'responsible catcher for runner on third', 'RUN3_RESP_CAT_ID'),
 ('33', 'number of balls in plate appearance', 'PA_BALL_CT'),
 ('34', 'number of called balls in plate appearance', 'PA_CALLED_BALL_CT'),
 ('35', 'number of intentional balls in plate appearance', 'PA_INTENT_BALL_CT'),
 ('36', 'number of pitchouts in plate appearance', 'PA_PITCHOUT_BALL_CT'),
 ('37', 'number of pitches hitting batter in plate appearance', 'PA_HITBATTER_BALL_CT'),
 ('38', 'number of other balls in plate appearance', 'PA_OTHER_BALL_CT'),
 ('39', 'number of strikes in plate appearance', 'PA_STRIKE_CT'),
 ('40', 'number of called strikes in plate appearance', 'PA_CALLED_STRIKE_CT'),
 ('41', 'number of swinging strikes in plate appearance', 'PA_SWINGMISS_STRIKE_CT'),
 ('42', 'number of foul balls in plate appearance', 'PA_FOUL_STRIKE_CT'),
 ('43', 'number of balls in play in plate appearance', 'PA_INPLAY_STRIKE_CT'),
 ('44', 'number of other strikes in plate appearance', 'PA_OTHER_STRIKE_CT'),
 ('45', 'number of runs on play', 'EVENT_RUNS_CT'),
 ('46', 'id of player fielding batted ball', 'FLD_ID'),
 ('47', 'force play at second flag', 'BASE2_FORCE_FL'),
 ('48', 'force play at third flag', 'BASE3_FORCE_FL'),
 ('49', 'force play at home flag', 'BASE4_FORCE_FL'),
 ('50', 'batter safe on error flag', 'BAT_SAFE_ERR_FL'),
 ('51', 'fate of batter', 'BAT_FATE_ID'),  # (base ultimately advanced to)
 ('52', 'fate of runner on first', 'RUN1_FATE_ID'),
 ('53', 'fate of runner on second', 'RUN2_FATE_ID'),
 ('54', 'fate of runner on third', 'RUN3_FATE_ID'),
 ('55', 'runs scored in half inning after this event', 'FATE_RUNS_CT'),
 ('56', 'fielder with sixth assist', 'ASS6_FLD_CD'),
 ('57', 'fielder with seventh assist', 'ASS7_FLD_CD'),
 ('58', 'fielder with eighth assist', 'ASS8_FLD_CD'),
 ('59', 'fielder with ninth assist', 'ASS9_FLD_CD'),
 ('60', 'fielder with tenth assist', 'ASS10_FLD_CD'),
 ('61', 'unknown fielding credit flag', 'UNKNOWN_OUT_EXC_FL'),
 ('62', 'uncertain play flag', 'UNCERTAIN_PLAY_EXC_FL')]

pitches = [('+', 'following pickoff throw by the catcher'),
 ('*', 'indicates the following pitch was blocked by the catcher'),
 ('.', 'marker for play not involving the batter'),
 ('1', 'pickoff throw to first'),
 ('2', 'pickoff throw to second'),
 ('3', 'pickoff throw to third'),
 ('>', 'Indicates a runner going on the pitch'),
 ('B', 'ball'),
 ('C', 'called strike'),
 ('F', 'foul'),
 ('H', 'hit batter'),
 ('I', 'intentional ball'),
 ('K', 'strike (unknown type)'),
 ('L', 'foul bunt'),
 ('M', 'missed bunt attempt'),
 ('N', 'no pitch (on balks and interference calls)'),
 ('O', 'foul tip on bunt'),
 ('P', 'pitchout'),
 ('Q', 'swinging on pitchout'),
 ('R', 'foul ball on pitchout'),
 ('S', 'swinging strike'),
 ('T', 'foul tip'),
 ('U', 'unknown or missed pitch'),
 ('V', 'called ball because pitcher went to his mouth'),
 ('X', 'ball put into play by batter'),
 ('Y', 'ball put into play on pitchout')]

game_info_fields = [#('id', 'ID'),
                    ('season_id', 'SEASON_ID'),
                    ('league_id', 'LEAGUE_ID'),
                    ('game_id', 'GAME_ID'),
                    ('game_dt', 'GAME_DT'),
                    ('game_ct', 'GAME_CT'),
                    ('game_dy', 'GAME_DY'),
                    ('start_game_tm', 'START_GAME_TM'),
                    ('dh_fl', 'DH_FL'),
                    ('daynight_park_cd', 'DAYNIGHT_PARK_CD'),
                    ('away_team_id', 'AWAY_TEAM_ID'),
                    ('home_team_id', 'HOME_TEAM_ID'),
                    ('park_id', 'PARK_ID'),
                    ('away_start_pit_id', 'AWAY_START_PIT_ID'),
                    ('home_start_pit_id', 'HOME_START_PIT_ID'),
                    ('base4_ump_id', 'BASE4_UMP_ID'),
                    ('base1_ump_id', 'BASE1_UMP_ID'),
                    ('base2_ump_id', 'BASE2_UMP_ID'),
                    ('base3_ump_id', 'BASE3_UMP_ID'),
                    ('lf_ump_id', 'LF_UMP_ID'),
                    ('rf_ump_id', 'RF_UMP_ID'),
                    ('attend_park_ct', 'ATTEND_PARK_CT'),
                    ('scorer_record_id', 'SCORER_RECORD_ID'),
                    ('translator_record_id', 'TRANSLATOR_RECORD_ID'),
                    ('inputter_record_id', 'INPUTTER_RECORD_ID'),
                    ('input_record_ts', 'INPUT_RECORD_TS'),
                    ('edit_record_ts', 'EDIT_RECORD_TS'),
                    ('method_record_cd', 'METHOD_RECORD_CD'),
                    ('pitches_record_cd', 'PITCHES_RECORD_CD'),
                    ('temp_park_ct', 'TEMP_PARK_CT'),
                    ('wind_direction_park_cd', 'WIND_DIRECTION_PARK_CD'),
                    ('wind_speed_park_ct', 'WIND_SPEED_PARK_CT'),
                    ('field_park_cd', 'FIELD_PARK_CD'),
                    ('precip_park_cd', 'PRECIP_PARK_CD'),
                    ('sky_park_cd', 'SKY_PARK_CD'),
                    ('minutes_game_ct', 'MINUTES_GAME_CT'),
                    ('inn_ct', 'INN_CT'),
                    ('away_score_ct', 'AWAY_SCORE_CT'),
                    ('home_score_ct', 'HOME_SCORE_CT'),
                    ('away_hits_ct', 'AWAY_HITS_CT'),
                    ('home_hits_ct', 'HOME_HITS_CT'),
                    ('away_err_ct', 'AWAY_ERR_CT'),
                    ('home_err_ct', 'HOME_ERR_CT'),
                    ('away_lob_ct', 'AWAY_LOB_CT'),
                    ('home_lob_ct', 'HOME_LOB_CT'),
                    ('win_pit_id', 'WIN_PIT_ID'),
                    ('lose_pit_id', 'LOSE_PIT_ID'),
                    ('save_pit_id', 'SAVE_PIT_ID'),
                    ('gwrbi_bat_id', 'GWRBI_BAT_ID'),
                    ('away_lineup1_bat_id', 'AWAY_LINEUP1_BAT_ID'),
                    ('away_lineup1_fld_cd', 'AWAY_LINEUP1_FLD_CD'),
                    ('away_lineup2_bat_id', 'AWAY_LINEUP2_BAT_ID'),
                    ('away_lineup2_fld_cd', 'AWAY_LINEUP2_FLD_CD'),
                    ('away_lineup3_bat_id', 'AWAY_LINEUP3_BAT_ID'),
                    ('away_lineup3_fld_cd', 'AWAY_LINEUP3_FLD_CD'),
                    ('away_lineup4_bat_id', 'AWAY_LINEUP4_BAT_ID'),
                    ('away_lineup4_fld_cd', 'AWAY_LINEUP4_FLD_CD'),
                    ('away_lineup5_bat_id', 'AWAY_LINEUP5_BAT_ID'),
                    ('away_lineup5_fld_cd', 'AWAY_LINEUP5_FLD_CD'),
                    ('away_lineup6_bat_id', 'AWAY_LINEUP6_BAT_ID'),
                    ('away_lineup6_fld_cd', 'AWAY_LINEUP6_FLD_CD'),
                    ('away_lineup7_bat_id', 'AWAY_LINEUP7_BAT_ID'),
                    ('away_lineup7_fld_cd', 'AWAY_LINEUP7_FLD_CD'),
                    ('away_lineup8_bat_id', 'AWAY_LINEUP8_BAT_ID'),
                    ('away_lineup8_fld_cd', 'AWAY_LINEUP8_FLD_CD'),
                    ('away_lineup9_bat_id', 'AWAY_LINEUP9_BAT_ID'),
                    ('away_lineup9_fld_cd', 'AWAY_LINEUP9_FLD_CD'),
                    ('home_lineup1_bat_id', 'HOME_LINEUP1_BAT_ID'),
                    ('home_lineup1_fld_cd', 'HOME_LINEUP1_FLD_CD'),
                    ('home_lineup2_bat_id', 'HOME_LINEUP2_BAT_ID'),
                    ('home_lineup2_fld_cd', 'HOME_LINEUP2_FLD_CD'),
                    ('home_lineup3_bat_id', 'HOME_LINEUP3_BAT_ID'),
                    ('home_lineup3_fld_cd', 'HOME_LINEUP3_FLD_CD'),
                    ('home_lineup4_bat_id', 'HOME_LINEUP4_BAT_ID'),
                    ('home_lineup4_fld_cd', 'HOME_LINEUP4_FLD_CD'),
                    ('home_lineup5_bat_id', 'HOME_LINEUP5_BAT_ID'),
                    ('home_lineup5_fld_cd', 'HOME_LINEUP5_FLD_CD'),
                    ('home_lineup6_bat_id', 'HOME_LINEUP6_BAT_ID'),
                    ('home_lineup6_fld_cd', 'HOME_LINEUP6_FLD_CD'),
                    ('home_lineup7_bat_id', 'HOME_LINEUP7_BAT_ID'),
                    ('home_lineup7_fld_cd', 'HOME_LINEUP7_FLD_CD'),
                    ('home_lineup8_bat_id', 'HOME_LINEUP8_BAT_ID'),
                    ('home_lineup8_fld_cd', 'HOME_LINEUP8_FLD_CD'),
                    ('home_lineup9_bat_id', 'HOME_LINEUP9_BAT_ID'),
                    ('home_lineup9_fld_cd', 'HOME_LINEUP9_FLD_CD'),
                    ('away_finish_pit_id', 'AWAY_FINISH_PIT_ID'),
                    ('home_finish_pit_id', 'HOME_FINISH_PIT_ID')]

def print_pitch_constants():
    for p in pitches:
        print "%s = '%s'" % (p[1].upper().replace(' ', '_'), p[0])


def print_attribute_list():
    """
    This function was used to print out the attribute setup code for GameState
    """
    atts = [field[1].lower().replace(' ', '_') for field in cw_event_fields]
    for a in atts:
        print ' ' * 8 + 'self.%s = None' % a

    atts = [field[1].lower().replace(' ', '_') for field in cw_event_fields_extended]
    for a in atts:
        print ' ' * 8 + 'self.%s = None' % a


def lookup_dict():
    ed = dict((field[1].lower().replace(' ', '_'), field[2]) for field in cw_event_fields)
    eed = dict((field[1].lower().replace(' ', '_'), field[2]) for field in cw_event_fields_extended)
    return dict(ed.items() + eed.items())


def print_model():
    """
    This function was used to print out the attribute setup code for GameState
    """
    atts = [field[2] for field in cw_event_fields]
    for a in atts:
        print ' ' * 8 + 'self.%s = None' % a

    atts = [field[2] for field in cw_event_fields_extended]
    for a in atts:
        print ' ' * 8 + 'self.%s = None' % a
