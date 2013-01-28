import logging
import webbrowser
from bs4 import BeautifulSoup
import commandlineoptions

import pointstreakscraper as pss
import setuplogger
import scrapetools
import manager

parser = commandlineoptions.parser
options = parser.parse_args()

rootlogger = setuplogger.setupRootLogger(options.log)
logger = logging.getLogger("main")

#===============================================================================
# temporary code to grab all the CCL playoff game ids
#===============================================================================
playoff = scrapetools.get_cached_url(pss.PS_2012_CCL_PLAYOFF_URL, pss.LISTINGS_CACHE_PATH % "PS_CCL_PLAYOFF_2012")
playoff_soup = BeautifulSoup(playoff)
links = playoff_soup.find_all("a")
scores = [l for l in links if l.text == "final"]
playoff_gameids = [s.attrs["href"].split('=')[1] for s in scores]

#===========================================================================
# instance parser, setup databse
#===========================================================================
games = {}
session = manager.init_database()

# track parsing success game ids
success_games = []
failed_games = []

for gameid in playoff_gameids:
    print gameid
    try:
        game, review_url= manager.build_game(gameid)
        for event in game.events():
            session.add(event)
        session.commit()
        games[game.game_id] = game
        success_games.append(game.game_id)
    except Exception, e:
        logger.exception("Error in Game %s in %s of inning %s" % (game.game_id, game.get_half_string(), game.inning))
        failed_games.append(game.game_id)
        if raw_input("show_problem_page?") == 'y':
            webbrowser.open_new_tab(review_url)
        raise

#===============================================================================
# Report Summary
#===============================================================================
print "PARSING COMPLETE"
print "Success count: {}".format(len(success_games))
print "Fail count: {}".format(len(failed_games))
