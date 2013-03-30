class PITCH_CHARS:
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


class PLAYS:
    FLY_BALL_BUNT = 'BF'
    GROUND_BALL_BUNT = 'BG'
    BUNT_GROUNDED_INTO_DOUBLE_PLAY = 'BGDP'
    LINE_DRIVE_BUNT = 'BL'
    BUNT_POP_UP = 'BP'
    BUNT_POPPED_INTO_DOUBLE_PLAY = 'BPDP'
    RUNNER_HIT_BY_BATTED_BALL = 'BR'
    CALLED_THIRD_STRIKE = 'C'
    UNSPECIFIED_DOUBLE_PLAY = 'DP'
    ERROR_ON = 'E'
    FLY = 'F'
    FLY_BALL_DOUBLE_PLAY = 'FDP'
    FOUL = 'FL'
    FORCE_OUT = 'FO'
    GROUND_BALL = 'G'
    GROUND_BALL_DOUBLE_PLAY = 'GDP'
    GROUND_BALL_TRIPLE_PLAY = 'GTP'
    INTERFERENCE = 'INT'
    LINE_DRIVE = 'L'
    LINED_INTO_DOUBLE_PLAY = 'LDP'
    LINED_INTO_TRIPLE_PLAY = 'LTP'
    POP_FLY = 'P'
    RELAY_THROW_FROM_THE_INITIAL_FIELDER_WITH_NO_OUT_MADE = 'R'
    SACRIFICE_FLY = 'SF'
    SACRIFICE_HIT = 'SH'
    THROW = 'TH'
    THROW_TO_BASE = 'TH'
    UNSPECIFIED_TRIPLE_PLAY = 'TP'


POSITION_LOOKUP = {"p": "P",
                   "pr": "P",
                   "pitching": "P",
                  "pitcher": "P",
                  1: "P",
                  '1': "P",
                  "c": "C",
                  "catching": "C",
                  "catcher": "C",
                  2: "C",
                  '2': "C",
                  "first base": "1B",
                  "first baseman": "1B",
                  "1b": "1B",
                  "1st base": "1B",
                  "1st": "1B",
                  3: "1B",
                  '3': "1B",
                  "2b": "2B",
                  "second base": "2B",
                  "second baseman": "2B",
                  "2nd base": "2B",
                  "2nd": "2B",
                  4: "2B",
                  '4': "2B",
                  "3b": "3B",
                  "third base": "3B",
                  "third baseman": "3B",
                  "3rd base": "3B",
                  "3rd": "3B",
                  5: "3B",
                  '5': "3B",
                  "ss": "SS",
                  "short stop": "SS",
                  "shortstop": "SS",
                  "short": "SS",
                  6: "SS",
                  '6': "SS",
                  "lf": "LF",
                  "left field": "LF",
                  "left fielder": "LF",
                  "left": "LF",
                  7: "LF",
                  '7': "LF",
                  "cf": "CF",
                  "center field": "CF",
                  "center fielder": "CF",
                  "center": "CF",
                  8: "CF",
                  '8': "CF",
                  "rf": "RF",
                  "right field": "RF",
                  "right fielder": "RF",
                  "right": "RF",
                  9: "RF",
                  '9': "RF",
                  "dh": "DH",
                  "designated hitter": "DH",
                  10: "DH",
                  '10': "DH",
                  "pinch hitter": "PH",
                  "ph": "PH",
                  11: "PH",
                  '11': "PH",
                  "pinch runner": "PR",
                  "pr": "PR",
                  12: "PR",
                  '12': "PR"
                  }
POSITIONS = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]
DH = "DH"
P = "P"

POSITION_CODES = {"P": 1,
                  "C": 2,
                  "1B": 3,
                  "2B": 4,
                  "3B": 5,
                  "SS": 6,
                  "LF": 7,
                  "CF": 8,
                  "RF": 9,
                  "DH": 10,
                  "PH": 11,
                  "PR": 12}

BASE_LOOKUP = {1: 1,
               "1st base": 1,
               "1st": 1,
               "first": 1,
               "first base": 1,
               2: 2,
               "2nd base": 2,
               "2nd": 2,
               "second": 2,
               "second base": 2,
               3: 3,
               "3rd base": 3,
               "3rd": 3,
               "third": 3,
               "third base": 3,
               4: 4,
               "home": 4,
               "home plate": 4
               }
TOP = 0
BOTTOM = 1

RIGHT = 'R'
LEFT = 'L'
SWITCH = 'S'
UNKNOWN = '?'


class EVENT_CODE:
    #UNKNOWN_(OBSOLETE) = 0
    #NONE_(OBSOLETE) = 1
    GENERIC_OUT = 2
    STRIKEOUT = 3
    STOLEN_BASE = 4
    DEFENSIVE_INDIFFERENCE = 5
    CAUGHT_STEALING = 6
    #PICKOFF_ERROR_(OBSOLETE) = 7
    PICKOFF = 8
    WILD_PITCH = 9
    PASSED_BALL = 10
    BALK = 11
    OTHER_ADVANCE = 12
    FOUL_ERROR = 13
    WALK = 14
    INTENTIONAL_WALK = 15
    HIT_BY_PITCH = 16
    INTERFERENCE = 17
    ERROR = 18
    FIELDERS_CHOICE = 19
    SINGLE = 20
    DOUBLE = 21
    TRIPLE = 22
    HOME_RUN = 23
    #MISSING_PLAY_(OBSOLETE) = 24


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
    BASE = "base"
    DESCRIPTION = "description"
    ERROR = "error"
    ERROR_TYPE = "error type"
    LOCATION = "location"
    NEW_PLAYER = "new player"
    PLAYER = "player"
    POSITION = "position"
    REPLACING = "replacing"
    UNKNOWN = "unknown"
    EARNED = "earned"
    UNEARNED = "unearned"


class PARSE_ADVANCE:
    DOUBLE = "double"
    FIELDERS_CHOICE = "fielders choice"
    GROUND_RULE = "ground rule"
    HIT_BY_PITCH = "hit by pitch"
    HOME_RUN = "home run"
    INTENTIONAL_WALK = "intentional walk"
    PASS_BALL = "pass ball"
    PLAYER_NUM = "player num"
    SINGLE = "single"
    STOLEN_BASE = "stolen base"
    THROW = "throw"
    TRIPLE = "triple"
    WALK = "walk"
    WILD_PITCH = "wild pitch"
    UNKNOWN = "unknown"
    DROPPED_THIRD_STRIKE = "dropped 3rd strike"
    BALK = "balk"
    EXTRA_BASES = "extra bases"

MAX_ASSIST_COUNT = 10
