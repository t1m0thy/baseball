import pyparsing as pp
import constants
from gamewrapper import GameWrapper

import logging
logger = logging.getLogger("pointstreak parser")


class PointStreakParser:
    """

    """
    def __init__(self, game=None, player_names=[]):
        self.gamewrap = GameWrapper(game)
        self.event_cache = []
        self.player_names = player_names
        self.setup_parser()

    def set_game(self, game):
        self.event_cache = []
        self.gamewrap.set_game(game)

    def setup_parser(self):
        #=======================================================================
        # Names
        #=======================================================================

        catch_all = pp.OneOrMore(pp.Word(pp.alphas+'-')).setResultsName(constants.PARSING_PLAYER.NAME)
        if self.player_names:
            player_no_num = pp.Keyword(self.player_names[0], caseless=True)
            for name in self.player_names[1:]:
                player_no_num |= pp.Keyword(name, caseless=True)
            for name in self.player_names:
                if "'" in name:
                    version = "&apos;".join(name.split("'"))
                    version2 = "_apos;".join(name.split("'"))
                    kw = pp.Keyword(version, caseless=True)
                    player_no_num |= kw
                    kw2 = pp.Keyword(version2, caseless=True)
                    player_no_num |= kw2
            player_no_num |= catch_all

        else:
            player_no_num = catch_all
        player_no_num = (player_no_num).setResultsName(constants.PARSING_PLAYER.NAME)
        player = (pp.Word(pp.nums).setResultsName(constants.PARSING_PLAYER.NUMBER) + \
            player_no_num).setResultsName(constants.PARSING.PLAYER)


        #===========================================================================
        # General Parser Items
        #===========================================================================

        dash = pp.Literal('-').suppress()
        left_paren = pp.Literal('(').suppress()
        right_paren = pp.Literal(')').suppress()
        period = pp.Literal('.').suppress()

        position = pp.Keyword("Pitcher", caseless=True) | \
            pp.Keyword("Catcher", caseless=True) | \
            pp.Keyword("First Baseman", caseless=True) | \
            pp.Keyword("Second Baseman", caseless=True) | \
            pp.Keyword("Third Baseman", caseless=True) | \
            pp.Keyword("ShortStop", caseless=True) | \
            pp.Keyword("Left Fielder", caseless=True) | \
            pp.Keyword("Center Fielder", caseless=True) | \
            pp.Keyword("Right Fielder", caseless=True)

        location = pp.Keyword("pitcher", caseless=True) | \
            pp.Keyword("Catcher", caseless=True) | \
            pp.Keyword("First Base", caseless=True) | \
            pp.Keyword("Second Base", caseless=True) | \
            pp.Keyword("Third Base", caseless=True) | \
            pp.Keyword("ShortStop", caseless=True) | \
            pp.Keyword("Left Field", caseless=True) | \
            pp.Keyword("Center Field", caseless=True) | \
            pp.Keyword("Right Field", caseless=True)

        #======================================================================
        # PITCHING
        #======================================================================
        pickoff_attempt = (pp.Keyword("Pickoff attempt at") +
                           pp.OneOrMore(pp.Word(pp.alphanums)).setResultsName(constants.PARSING.BASE) +
                            left_paren + pp.Optional(
                            position.setResultsName(constants.PARSE_PITCHING.THROW_POSITION) +
                            pp.Keyword("to")) +
                            position.setResultsName(constants.PARSE_PITCHING.CATCH_POSITION) +
                            right_paren
                           ).setParseAction(self.gamewrap.pickoff)
        swinging = pp.Keyword("Swinging Strike", caseless=True).setParseAction(self.gamewrap.swinging_strike)
        called = pp.Keyword("Called Strike", caseless=True).setParseAction(self.gamewrap.called_strike)
        ball = pp.Keyword("Ball", caseless=True).setParseAction(self.gamewrap.ball)
        foul = pp.Keyword("Foul", caseless=True).setParseAction(self.gamewrap.foul)
        error_e = pp.CaselessLiteral("E") + pp.Word(pp.nums).setResultsName(constants.PARSING.POSITION)
        dropped_foul = pp.Keyword("Dropped Foul", caseless=True) + pp.Optional(dash + error_e)
        pitches = dropped_foul | swinging | called | ball | foul | pickoff_attempt
        #===============================================================================
        #  Outs
        #===============================================================================
        foul = pp.Optional(pp.CaselessLiteral('F').setResultsName(constants.PARSING_OUTS.FOUL))
        pop = pp.CaselessLiteral("P") + pp.Word(pp.nums).setResultsName(constants.PARSING.POSITION)
        unassisted_out = (pp.Word(pp.nums).setResultsName(constants.PARSING.POSITION) + pp.CaselessLiteral("U")).setResultsName(constants.PARSING_OUTS.UNASSISTED)
        line_drive = (pp.CaselessLiteral("L") + pp.Word(pp.nums).setResultsName(constants.PARSING.POSITION) + foul).setResultsName(constants.PARSING_OUTS.LINE_DRIVE)
        popup = ((foul + pop) | (pop + foul)).setResultsName(constants.PARSING_OUTS.POPUP)
        thrown_out = (pp.delimitedList(pp.Word(pp.nums), "-")+pp.Optional(dash)).setResultsName(constants.PARSING_OUTS.THROWN_OUT)
        double_play = pp.CaselessLiteral("DP").setResultsName(constants.PARSING_OUTS.DOUBLE_PLAY)
        triple_play = pp.CaselessLiteral("TP").setResultsName(constants.PARSING_OUTS.TRIPLE_PLAY)
        picked_off = pp.CaselessLiteral("PO").setResultsName(constants.PARSING_OUTS.PICK_OFF)
        sacrifice_hit = pp.CaselessLiteral("SH").setResultsName(constants.PARSING_OUTS.SACRIFICE)
        dropped_third_strike = (pp.CaselessLiteral("KS")).setResultsName(constants.PARSING_OUTS.DROPPED_THIRD)
        caught_stealing = (pp.CaselessLiteral("CS")).setResultsName(constants.PARSING_OUTS.CAUGHT_STEALING)
        strike_out = ((pp.Keyword("Strike Out", caseless=True) +
                       pp.Optional(pp.Keyword("swinging")).setResultsName(constants.PARSING_OUTS.SWINGING)) | \
                      (pp.CaselessLiteral("K") + pp.Optional(double_play))
                      ).setResultsName(constants.PARSING_OUTS.STRIKE_OUT)
        fly_out = (pp.Keyword("Fly out to", caseless=True) + pp.Optional(pp.Keyword("the")) +
                   (position | location).setResultsName(constants.PARSING.POSITION) +
                   pp.Optional(pp.Keyword("in foul territory", caseless=True).setResultsName(constants.PARSING_OUTS.FOUL))
                   ).setResultsName(constants.PARSING_OUTS.FLY_OUT)

        sacrifice_fly = (pp.Keyword("sacrifice fly to", caseless=True).setResultsName(constants.PARSING_OUTS.SACRIFICE)
                         + position.setResultsName(constants.PARSING.POSITION)).setResultsName(constants.PARSING_OUTS.FLY_OUT)
        possibles = double_play | triple_play | \
                    picked_off | \
                    sacrifice_hit | \
                    dropped_third_strike | \
                    caught_stealing | \
                    thrown_out | \
                    unassisted_out | \
                    strike_out | \
                    fly_out | \
                    sacrifice_fly | \
                    line_drive | \
                    popup

        out_description = (left_paren +
                           pp.OneOrMore(possibles | pp.Word(pp.alphanums + ':')) +
                           right_paren).setResultsName(constants.PARSING.DESCRIPTION)

        putout = (player + pp.Keyword("putout", caseless=True) + pp.Optional(out_description)).setParseAction(self.gamewrap.put_out) + pp.Keyword("for out number") + pp.Word(pp.nums)

        #===============================================================================
        # Advancing
        #===============================================================================
        base = pp.OneOrMore(pp.Word(pp.alphanums)).setResultsName(constants.PARSING.BASE)
        hit_location = pp.Keyword("to") + pp.Optional(pp.Keyword("the")) + location.setResultsName(constants.PARSING.LOCATION)
        position_number = pp.Word(pp.nums).setResultsName(constants.PARSING.LOCATION)
        wild_pitch = pp.Keyword("wild pitch", caseless=True).setResultsName(constants.PARSE_ADVANCE.WILD_PITCH)

        single = ((pp.Keyword("single", caseless=True) +
                  pp.Optional(hit_location) | \
                  (pp.Keyword("1B").setResultsName(constants.PARSE_ADVANCE.EXTRA_BASES) + position_number))
                  ).setResultsName(constants.PARSE_ADVANCE.SINGLE)
        double = (pp.Keyword("double", caseless=True) +
                  pp.Optional(hit_location)
                  ).setResultsName(constants.PARSE_ADVANCE.DOUBLE)
        triple = (pp.Keyword("triple", caseless=True) +
                  pp.Optional(hit_location)
                  ).setResultsName(constants.PARSE_ADVANCE.TRIPLE)
        home_run = (pp.Keyword("home run", caseless=True) +
                  pp.Optional(hit_location)
                  ).setResultsName(constants.PARSE_ADVANCE.HOME_RUN)
        balk = pp.Keyword("balk", caseless=True).setResultsName(constants.PARSE_ADVANCE.BALK)
        dropped_third_strike = pp.Keyword("dropped 3rd strike", caseless=True).setResultsName(constants.PARSE_ADVANCE.DROPPED_THIRD_STRIKE)
        fielders_choice = pp.Keyword("fielder's choice", caseless=True).setResultsName(constants.PARSE_ADVANCE.FIELDERS_CHOICE)
        hit_by_pitch = pp.Keyword("hit by pitch", caseless=True).setResultsName(constants.PARSE_ADVANCE.HIT_BY_PITCH)
        walk = pp.Keyword("walk", caseless=True).setResultsName(constants.PARSE_ADVANCE.WALK)
        stolen_base = ((pp.Word(pp.nums) + pp.Keyword("SB", caseless=True)) | pp.Keyword("stolen base", caseless=True)).setResultsName(constants.PARSE_ADVANCE.STOLEN_BASE)
        error = ((pp.Keyword("error by the") + position.setResultsName(constants.PARSING.POSITION)
                  ) | \
                (pp.Optional(pp.Keyword("SAC", caseless=True)) + pp.Optional(pp.Word(pp.nums)) +
                 pp.CaselessLiteral("e") +
                 pp.oneOf("1 2 3 4 5 6 7 8 9").setResultsName(constants.PARSING.POSITION) +
                 # Fielder ERror, Throwing Error, Muffed (poorly caught between fielders)
                 pp.Optional(pp.CaselessLiteral("F") | pp.CaselessLiteral("D") | pp.CaselessLiteral("T") | pp.CaselessLiteral("M") ).setResultsName(constants.PARSING.ERROR_TYPE) +
                 pp.Optional(pp.Word(pp.nums))
                )
                ).setResultsName(constants.PARSING.ERROR)

        pass_ball = pp.Keyword("pass ball", caseless=True).setResultsName(constants.PARSE_ADVANCE.PASS_BALL)
        ground_rule = (pp.Keyword("ground rule", caseless=True) +
                       pp.oneOf("single double triple", caseless=True)
                       ).setResultsName(constants.PARSE_ADVANCE.GROUND_RULE)
        throw = (pp.Literal("T") + pp.Optional(pp.Word(pp.nums))).setResultsName(constants.PARSE_ADVANCE.THROW)
        intentional_walk = pp.Keyword("intentional walk", caseless=True).setResultsName(constants.PARSE_ADVANCE.INTENTIONAL_WALK)
        player_num = pp.Word(pp.nums).setResultsName(constants.PARSE_ADVANCE.PLAYER_NUM) + \
                    pp.Optional(pp.Keyword("throw", caseless=True) | pp.Keyword("T") |  error |  pp.Keyword("bu") | pp.Keyword("cs"))
        unknown = pp.OneOrMore(pp.Word(pp.alphanums)).setResultsName(constants.PARSE_ADVANCE.UNKNOWN)
        empty = pp.Empty().setResultsName(constants.PARSE_ADVANCE.UNKNOWN)

        advance_desc = left_paren + (balk | wild_pitch | single | double | triple | home_run | dropped_third_strike | \
                                       fielders_choice | hit_by_pitch | throw | walk | stolen_base | \
                                       error | player_num | pass_ball | ground_rule | intentional_walk | unknown | empty
                                       ) + right_paren
        advances = (player +
                    pp.Keyword("advances to", caseless=True) +
                    base + advance_desc.setResultsName(constants.PARSING.DESCRIPTION)
                    ).setParseAction(self.gamewrap.parse_advance)

        #===========================================================================
        # Scoring
        #===========================================================================
        end_span = pp.Optional(pp.Literal('</span>')).suppress()
        earned_span = pp.Optional(pp.Literal('<span class="earned">')).suppress()
        unearned_span = pp.Optional(pp.Literal('<span class="unearned">')).suppress()
        score_span = pp.Optional(pp.Literal('<span class="score">')).suppress()
        earned = earned_span + pp.Keyword("Earned", caseless=True).setResultsName(constants.PARSING.EARNED) + \
                    end_span + advance_desc.setResultsName(constants.PARSING.DESCRIPTION)
        unearned = unearned_span + pp.Keyword("Unearned", caseless=True).setResultsName(constants.PARSING.UNEARNED) + \
                    end_span + advance_desc.setResultsName(constants.PARSING.DESCRIPTION)
        score_word = score_span + pp.Keyword("Scores", caseless=True) + end_span
        scores = (player + score_word + (unearned | earned)).setParseAction(self.gamewrap.parse_score)

        #======================================================================
        # SUBS
        #======================================================================
        replacing = player_no_num.setResultsName(constants.PARSING.REPLACING)
        new_player = player.setResultsName(constants.PARSING.NEW_PLAYER)
        position = pp.OneOrMore(pp.Word(pp.alphanums))
        defensive_sub = pp.Keyword("Defensive Substitution.") + new_player + \
                        pp.Optional(
                            ((pp.Keyword("subs for") + replacing + pp.Keyword("at")) | \
                            pp.Keyword("moves to") | \
                            pp.Keyword("subs at")
                            ) + \
                            position.setResultsName(constants.PARSING.POSITION)
                        ) + period
        defensive_sub.setParseAction(self.gamewrap.parse_defensive_sub)
        dh_sub = pp.Keyword("Defensive Substitution.") + new_player + \
                 pp.Keyword("subs for") + replacing + period
        dh_sub.setParseAction(self.gamewrap.parse_defensive_sub)

        pitching_sub = pp.Keyword("Pitching Substitution.") + new_player + \
                       pp.Optional(
                        (pp.Keyword("subs for") + replacing.setResultsName(constants.PARSING.REPLACING)) | \
                        (pp.Keyword("moves to", caseless=True) + position.setResultsName(constants.PARSING.POSITION))
                        ) + period
        pitching_sub.setParseAction(self.gamewrap.parse_defensive_sub)
        self.pitching_sub = pitching_sub
        offensive_sub = pp.Keyword("Offensive Substitution.") + new_player + \
                        pp.Optional(pp.Keyword("subs for") + replacing) + period
        offensive_sub.setParseAction(self.gamewrap.parse_offensive_sub)
        runner_sub = pp.Keyword("Offensive Substitution.") + new_player + \
                     ((pp.Keyword("runs for") + replacing) | pp.Keyword("subs")) + pp.Keyword("at") + \
                     pp.Word(pp.alphanums).setResultsName(constants.PARSING.BASE) + pp.Word(pp.alphanums) + period
        runner_sub.setParseAction(self.gamewrap.parse_offensive_sub)
        subs = defensive_sub | dh_sub | pitching_sub | offensive_sub | runner_sub
        #===========================================================================
        # Summary
        #===========================================================================
        self.event_parser = (subs + pp.StringEnd()) | (pp.delimitedList(pitches | advances | putout | scores) + pp.StringEnd().setParseAction(self.gamewrap.event_complete))

    def parse_event(self, text):
        self.last_event_text = text
        self.event_cache.append(text)
        self.event_parser.parseString(text)
        return self.gamewrap._game
