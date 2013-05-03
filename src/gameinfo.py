import datetime
import eventfields
from models import gameinfomodel
from constants import POSITION_CODES


class GameInfo:
    def __init__(self, gameid):
        self.game_id = gameid
        self.game_dt = ""
        self.game_ct = 0
        self.game_dy = ""
        self.start_game_tm = ""
        self.dh_fl = ""
        self.daynight_park_cd = 0
        self.away_team_id = ""
        self.home_team_id = ""
        self.park_id = ""
        self.away_start_pit_id = ""
        self.home_start_pit_id = ""
        self.base4_ump_id = ""
        self.base1_ump_id = ""
        self.base2_ump_id = ""
        self.base3_ump_id = ""
        self.lf_ump_id = ""
        self.rf_ump_id = ""
        self.attend_park_ct = 0

        self.scorer_record_id = ""
        self.translator_record_id = ""
        self.inputter_record_id = ""
        self.input_record_ts = ""
        self.edit_record_ts = ""

        self.method_record_cd = 0
        self.pitches_record_cd = 0

        self.temp_park_ct = 0
        self.wind_direction_park_cd = 0
        self.wind_speed_park_ct = 0
        self.field_park_cd = 0
        self.precip_park_cd = 0
        self.sky_park_cd = 0

        self.minutes_game_ct = 0
        self.inn_ct = 0

        self.away_score_ct = 0
        self.home_score_ct = 0
        self.away_hits_ct = 0
        self.home_hits_ct = 0
        self.away_err_ct = 0
        self.home_err_ct = 0
        self.away_lob_ct = 0
        self.home_lob_ct = 0
        self.win_pit_id = ""
        self.lose_pit_id = ""
        self.save_pit_id = ""
        self.gwrbi_bat_id = ""

        self.away_lineup1_bat_id = ""
        self.away_lineup1_fld_cd = 0
        self.away_lineup2_bat_id = ""
        self.away_lineup2_fld_cd = 0
        self.away_lineup3_bat_id = ""
        self.away_lineup3_fld_cd = 0
        self.away_lineup4_bat_id = ""
        self.away_lineup4_fld_cd = 0
        self.away_lineup5_bat_id = ""
        self.away_lineup5_fld_cd = 0
        self.away_lineup6_bat_id = ""
        self.away_lineup6_fld_cd = 0
        self.away_lineup7_bat_id = ""
        self.away_lineup7_fld_cd = 0
        self.away_lineup8_bat_id = ""
        self.away_lineup8_fld_cd = 0
        self.away_lineup9_bat_id = ""
        self.away_lineup9_fld_cd = 0
        self.home_lineup1_bat_id = ""
        self.home_lineup1_fld_cd = 0
        self.home_lineup2_bat_id = ""
        self.home_lineup2_fld_cd = 0
        self.home_lineup3_bat_id = ""
        self.home_lineup3_fld_cd = 0
        self.home_lineup4_bat_id = ""
        self.home_lineup4_fld_cd = 0
        self.home_lineup5_bat_id = ""
        self.home_lineup5_fld_cd = 0
        self.home_lineup6_bat_id = ""
        self.home_lineup6_fld_cd = 0
        self.home_lineup7_bat_id = ""
        self.home_lineup7_fld_cd = 0
        self.home_lineup8_bat_id = ""
        self.home_lineup8_fld_cd = 0
        self.home_lineup9_bat_id = ""
        self.home_lineup9_fld_cd = 0

        self.away_finish_pit_id = ""
        self.home_finish_pit_id = ""

    def as_model(self):
        m = gameinfomodel.GameInfoModel()
        for att, model_att in eventfields.game_info_fields:
            setattr(m, model_att, getattr(self, att))
        return m

    def _set_date(self, date):
        self.game_dt = int(date.strftime("%y%m%d"))
        self.game_dy = date.strftime("%A")
        self.start_game_tm = int(date.strftime("%I%M"))

        if int(date.strftime("%H")) > 17:
            self.daynight_park_cd = 'N'
        else:
            self.daynight_park_cd = 'D'

    def set_game_info(self, game_info):
        start_date_time = datetime.datetime.strptime(game_info.get("Date", "") + ", " + game_info.get("Time", ""),
                                                     "%A, %B %d %Y, %I:%M %p")
        end_date_time = datetime.datetime.strptime(game_info.get("EndDate", "") + ", " + game_info.get("EndTime", ""),
                                                   "%m/%d/%Y, %I:%M %p")

        self.away_team_id = game_info.get("VisitingTeam")
        self.home_team_id = game_info.get("HomeTeam")

        self._set_date(start_date_time)
        duration = end_date_time - start_date_time

        self.park_id = game_info.get("Location")
        self.base4_ump_id = game_info.get("PlateUmp", "")
        self.base1_ump_id = game_info.get("Ump1", "")
        self.base3_ump_id = game_info.get("Ump3", "")

        # These probably don't exist:
        self.base2_ump_id = game_info.get("Ump2", "")
        self.lf_ump_id = game_info.get("UmpLF", "")
        self.rf_ump_id = game_info.get("UmpRF", "")

        self.minutes_game_ct = duration.seconds / 60
        self.inn_ct = game_info.get("EndLastInningScored")

        self.attend_park_ct = game_info.get("Attendance")

    def set_starting_players(self, away_lineup, home_lineup):
        #self.game_id = self.game_id

        try:
            home_lineup.find_player_by_position("DH")
            self.dh_fl = True
        except KeyError:
            self.dh_fl = False

        self.away_start_pit_id = away_lineup.find_player_by_position("P").name.id()
        self.home_start_pit_id = home_lineup.find_player_by_position("P").name.id()

        for order in range(1, 10):
            player = away_lineup.find_player_by_order(order)
            setattr(self, "away_lineup{}_bat_id", player.name.id())
            setattr(self, "away_lineup{}_fld_cd", POSITION_CODES[player.position])

            player = home_lineup.find_player_by_order(order)
            setattr(self, "home_lineup{}_bat_id", player.name.id())
            setattr(self, "home_lineup{}_fld_cd", POSITION_CODES[player.position])
