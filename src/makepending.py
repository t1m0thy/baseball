import scrapetools
from bs4 import BeautifulSoup
from jobmanager import JobManager
import os

def add_gameids_to_pending(output_filepath, cache_path):
    #===============================================================================
    # temporary code to grab all the CCL playoff game ids
    #===============================================================================
    LISTINGS_CACHE_PATH = os.path.join(cache_path, "listings","list_%s.html")
    PS_2012_CCL_PLAYOFF_URL = "http://www.pointstreak.com/baseball/schedule.html?leagueid=166&seasonid=18269"
    
    playoff = scrapetools.get_cached_url(PS_2012_CCL_PLAYOFF_URL, LISTINGS_CACHE_PATH % "PS_CCL_PLAYOFF_2012")
    playoff_soup = BeautifulSoup(playoff)
    links = playoff_soup.find_all("a")
    scores = [l for l in links if l.text == "final"]
    playoff_gameids = [s.attrs["href"].split('=')[1] for s in scores]
    jm = JobManager(output_filepath)    
    for gameid in playoff_gameids:
        jm.add_job(gameid, jobtype="pointstreak")
    jm.save()
        
if __name__ == "__main__":
    add_gameids_to_pending("pending.yml", "../htmlcache")
    
    
