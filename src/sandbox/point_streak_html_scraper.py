#@PydevCodeAnalysisIgnore

class PSPRawEvent(RawEvent):
    def __init__(self, title, text):
        self._title = title
        self._text = text

    def is_sub(self):
        return "substitution" in self._title.lower()

    def batter(self):
        if self.is_sub():
            return StandardError("No batter for substitution event")
        else:
            return ' '.join(self._title.split()[1:])

    def text(self):
        return self._text

class PSPHalfInningHTML(HalfInning):
    def __init__(self, pbp_string):
        self._pbp_string = pbp_string
        self._cleaned = [part.strip() for part in self._pbp_string.split('\t') if len(part.strip()) > 0]
        self.inning_name = self._cleaned.pop(0)
        self.batting_team = self._cleaned.pop(0)

    def raw_events(self):
        while len(self._cleaned) > 1:
            yield(PSPRawEvent(self._cleaned.pop(0), self._cleaned.pop(0)))

class PointStreakHTMLScraper(PointStreakScraper):
    def __init__(self, gameid):
        PointStreakScraper.__init__(self, gameid)
        html = self._get_pointstreak_game_html(gameid)
        soup = BeautifulSoup(html)
        self.divs = self._div_id_dict(soup)
        tds = self.divs[DIV_ID_GAME_SUMMARY].findAll("td")
        self._awayteam, self._hometeam = [td.text.strip() for td in tds if "psbb_box_score_team" in td.attrs.get("class", [])]

    def home_team(self):
        return self._hometeam

    def away_team(self):
        return self._awayteam

    def review_url(self):
        return self._get_point_streak_url()

    def halfs(self):
        pbp_div = self.divs[DIV_ID_PLAYBYPLAY]
        innings = [tr for tr in pbp_div.findAll("tr") if "inning" in tr.attrs.get("class",[])]
        halfs = [PSPHalfInningHTML(s.text) for s in innings]
        for h in halfs:
            yield h

    def _div_id_dict(self, element):
        return dict((d.attrs["id"], d) for d in element.findAll("div") if d.has_attr("id"))

    def game_roster(self):
        xml = self._get_pointstreak_xml()
        root = lxml.etree.fromstring(xml)

        away = root.find(".//{*}VisitingTeam")
        away_offense = [dict(e.items()) for e in away.find(".//{*}Offense").getchildren()]
        away_replaced = [dict(e.items()) for e in away.find(".//{*}ReplacedOffense").getchildren()]
        away_pitchers = [dict(e.items()) for e in away.find(".//{*}Pitchers").getchildren()]

        home = root.find(".//{*}HomeTeam")
        home_offense = [dict(e.items()) for e in home.find(".//{*}Offense").getchildren()]
        home_replaced = [dict(e.items()) for e in home.find(".//{*}ReplacedOffense").getchildren()]
        home_pitchers = [dict(e.items()) for e in home.find(".//{*}Pitchers").getchildren()]

        away_roster = dict([(d["Name"], d["PlayerId"]) for d in away_offense + away_replaced + away_pitchers])
        home_roster = dict([(d["Name"], d["PlayerId"]) for d in home_offense + home_replaced + home_pitchers])

        return away_roster, home_roster
