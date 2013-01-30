import pointstreakscraper as pss
from jobmanager import JobManager

PS_2012_PLAYOFF = 18269
PS_2012_SEASON = 12252

if __name__ == "__main__":
    regular_season_ids = pss.scrape_season_gameids(PS_2012_SEASON)
    post_season_ids = pss.scrape_season_gameids(PS_2012_PLAYOFF)
    jm = JobManager("jobs.yml")  
    jm.add_jobs(regular_season_ids, job_group="pointstreak")
    jm.add_jobs(post_season_ids, job_group="pointstreak")
    jm.save()
            
