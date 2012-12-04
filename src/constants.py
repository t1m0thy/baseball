FOLLOWING_PICKOFF_THROW_BY_THE_CATCHER = '+'
FOLLOWING_PITCH_WAS_BLOCKED_BY_THE_CATCHER = '*'
PLAY_NOT_INVOLVING_THE_BATTER = '.'
PICKOFF_THROW_TO_FIRST = '1'
PICKOFF_THROW_TO_SECOND = '2'
PICKOFF_THROW_TO_THIRD = '3'
A_RUNNER_GOING_ON_THE_PITCH = '>'
BALL = 'B'
CALLED_STRIKE = 'C'
FOUL = 'F'
HIT_BATTER = 'H'
INTENTIONAL_BALL = 'I'
STRIKE_UNKNOWN_TYPE = 'K'
FOUL_BUNT = 'L'
MISSED_BUNT_ATTEMPT = 'M'
NO_PITCH_ON_BALKS_AND_INTERFERENCE_CALLS = 'N'
FOUL_TIP_ON_BUNT = 'O'
PITCHOUT = 'P'
SWINGING_ON_PITCHOUT = 'Q'
FOUL_BALL_ON_PITCHOUT = 'R'
SWINGING_STRIKE = 'S'
FOUL_TIP = 'T'
UNKNOWN_OR_MISSED_PITCH = 'U'
CALLED_BALL_BECAUSE_PITCHER_WENT_TO_HIS_MOUTH = 'V'
BALL_PUT_INTO_PLAY_BY_BATTER = 'X'
BALL_PUT_INTO_PLAY_ON_PITCHOUT = 'Y'

POSITION_LOOKUP = {"P":"P",
                   "PR": "P",
                   "Pitching": "P", 
                  "Pitcher": "P",
                  "C":"C",
                  "Catching": "C",
                  "Catcher": "C",
                  "First Base": "1B",
                  "First Baseman": "1B",
                  "1B": "1B",
                  "1st Base": "1B",
                  "1st": "1B",
                  "2B": "2B",
                  "Second Base": "2B",
                  "Second Baseman": "2B",
                  "2nd Base": "2B",
                  "2nd": "2B",
                  "3B": "3B",
                  "Third Base": "3B",
                  "Third Baseman": "3B",
                  "3rd Base": "3B",
                  "3rd": "3B",
                  "SS": "SS",
                  "Short Stop": "SS",
                  "Short": "SS",
                  "LF": "LF",
                  "Left Field": "LF",
                  "Left Fielder": "LF",
                  "Left": "LF",
                  "CF": "CF",
                  "Center Field": "CF",
                  "Center Fielder": "CF",                  
                  "Center": "CF",
                  "RF": "RF",
                  "Right Field": "RF",
                  "Right Fielder": "RF",
                  "Right": "RF",
                  "DH": "DH",
                  "Designated Hitter": "DH",
                  "Pinch Hitter": "PH",
                  "PH": "PH"
                  }
POSITIONS = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]
DH = "DH"
P = "P"

POSITION_CODES = {"DH":10,
                  "PH":11,
                  "PR":12}

BASE_LOOKUP = {1:1,
               "1st base":1,
               "1st":1,
               "first":1,
               "first base":1,
               2:2,
               "2nd base":2,
               "2nd":2,
               "second":2,
               "second base":2,
               3:3,
               "3rd base":3,
               "3rd":3,
               "third":3,
               "third base":3,
               }
TOP = 0
BOTTOM = 1  

RIGHT = 'R'
LEFT = 'L'



#EVT_CODE_UNKNOWN_(OBSOLETE) = 0
#EVT_CODE_NONE_(OBSOLETE) = 1
EVT_CODE_GENERIC_OUT = 2
EVT_CODE_STRIKEOUT = 3
EVT_CODE_STOLEN_BASE = 4
EVT_CODE_DEFENSIVE_INDIFFERENCE = 5
EVT_CODE_CAUGHT_STEALING = 6
#EVT_CODE_PICKOFF_ERROR_(OBSOLETE) = 7
EVT_CODE_PICKOFF = 8
EVT_CODE_WILD_PITCH = 9
EVT_CODE_PASSED_BALL = 10
EVT_CODE_BALK = 11
EVT_CODE_OTHER_ADVANCE = 12
EVT_CODE_FOUL_ERROR = 13
EVT_CODE_WALK = 14
EVT_CODE_INTENTIONAL_WALK = 15
EVT_CODE_HIT_BY_PITCH = 16
EVT_CODE_INTERFERENCE = 17
EVT_CODE_ERROR = 18
EVT_CODE_FIELDERS_CHOICE = 19
EVT_CODE_SINGLE = 20
EVT_CODE_DOUBLE = 21
EVT_CODE_TRIPLE = 22
EVT_CODE_HOME_RUN = 23
#EVT_CODE_MISSING_PLAY_(OBSOLETE) = 24

class PARSING_OUTS:
    DOUBLE_PLAY = "double play"
    TRIPLE_PLAY = "double play"
    FLY_OUT = "fly out"
    STRIKE_OUT = "strike out"
    SACRIFICE = "sacrifice"
    THROWN_OUT = "thrown out"
    PICK_OFF = "pick off"
    DROPPED_THIRD = "dropped third"
    CAUGHT_STEALING = "caught stealing"
    SWINGING = "swinging"
    UNASSISTED = "unassisted"
    LINE_DRIVE = "L"
    POPUP = "P"
    FOUL = "F"
    OUT_COUNT = "out count"
    
class PARSING_PLAYER:
    NAME = "name"
    NUMBER = "number"
    
class PARSE_PITCHING:
    THROW_POSITION = "thrower"
    CATCH_POSITION = "pick catcher"
    
class PARSING:
    # TODO: fill out the rest of this class of parser token constants
    NEW_PLAYER = "new player"
    REPLACING = "replacing"
    POSITION = "position"
    PLAYER = "player"
    DESCRIPTION = "description"
    BASE = "base"
    LOCATION = "location"
    UNKNOWN = "unknown"

class PARSE_ADVANCE:
    INTENTIONAL_WALK = "intentional walk"
    PASS_BALL = "pass ball"
    GROUND_RULE = "ground rule"
    THROW = "throw"
    ERROR = "error"
    WILD_PITCH = "wild pitch"
    PLAYER_NUM = "player num"
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    FIELDERS_CHOICE = "fielders choice"
    HIT_BY_PITCH = "hit by pitch"