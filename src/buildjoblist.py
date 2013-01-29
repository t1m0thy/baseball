import scrapetools
from bs4 import BeautifulSoup
from jobmanager import JobManager
import os
import json

PS_2012_PLAYOFF = 18269
PS_2012_SEASON = 12252

PS_JSON_URL = "http://www.pointstreak.com/baseball/ajax/schedule_ajax.php?action=showalldates&s={}"
    
def scrape_pointstreak_gameids(html):
    playoff_soup = BeautifulSoup(html)
    links = playoff_soup.find_all("a")
    scores = [l for l in links if l.text == "final"]
    gameids = [s.attrs["href"].split('=')[1] for s in scores]
    return gameids

def add_season(output_filepath, cache_path, seasonid):
    LISTINGS_CACHE_PATH = os.path.join(cache_path, "listings","list_{}.json".format(seasonid))
    season = scrapetools.get_cached_url(PS_JSON_URL.format(seasonid), LISTINGS_CACHE_PATH)
    html = json.loads(season)["html"]
    ids = scrape_pointstreak_gameids(html)
    jm = JobManager(output_filepath)    
    jm.add_jobs(ids, jobtype="pointstreak")
    jm.save()
            
if __name__ == "__main__":
    add_season("jobs.yml", "../htmlcache", PS_2012_PLAYOFF)
    add_season("jobs.yml", "../htmlcache", PS_2012_SEASON)
    