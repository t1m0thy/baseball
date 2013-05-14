#!/usr/bin/env python

'''
Created on Feb 27, 2013

@author: Lefko
'''

import os
from bs4 import BeautifulSoup
import scrapetools

# some path setup to save the html files we download for future use
BASE_DIR = os.path.dirname(__file__)
DEFAULT_CACHE_PATH = os.path.join(BASE_DIR, "../htmlcache/")

# base url for stats based on id and type
PS_STATS_URL_BASE = "http://www.pointstreak.com/baseball/stats.html?seasonid={season_id}&view={stat_type}"


def get_stats_table(stat_type, season_id):
    """
    grab the stats table

    stat_type "pitching"|"batting"
    season_id = point streak season id.  string or int
    """
    cache_dir = os.path.join(DEFAULT_CACHE_PATH, "{}_stats".format(stat_type))
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)
    url = PS_STATS_URL_BASE.format(season_id=season_id, stat_type=stat_type)
    cache_file_path = os.path.join(cache_dir, "season_{}.html".format(season_id))
    html = scrapetools.get_cached_url(url, cache_file_path)
    soup = BeautifulSoup(html)
    table = soup.findAll("table", {'id': stat_type+'1'})
    return table


def stats_scraper(stat_type, columns, season_id, f):
    """
    stat_type = "pitching"|"batting"
    columns: the number columns to scrape from the table
    season_id: the ps season id
    f: an open file where to write the lines
    """

    table = get_stats_table(stat_type, season_id)
    for row in table[0]("tr"):
        col = row("td")

        if len(col) > 1:
            record = [str(season_id), col[0].a.text.strip()]
            try:
                player_id = col[0].a.attrs.get("href", "").split("=")[1]
                record += [player_id]
            except IndexError:
                record += "None"
            record += [col[i].text.strip() for i in range(1, columns)]
            print record
            line = ','.join(record) + "\n"
            f.write(line)


def scrape_pitch_stats(season_id, f):
    return stats_scraper("pitching", 17, season_id, f)


def scrape_hit_stats(season_id, f):
    return stats_scraper("batting", 21, season_id, f)

if __name__ == "__main__":
    season_list = [18269, 12252, 12218, 12493, 11467, 12561, 12547, 11944, 12238, 12193, 11943, 15900, 12222, 13006]

    # Create a CSV where we'll save our data.
    f = open('pshitstats.csv', 'w')
    # Add headers
    f.write("season_id, last, first, psid, team, p, avg, g, ab, r, h, d, t, hr, rbi, bb, hbp, so, sf, sh, sb, cs, dp, e\n")
    for season in season_list:
        print scrape_hit_stats(season,  f)
    f.close()

    f = open('pspitching.csv', 'w')
    # Add headers
    #(player, team, g, gs, cg, ip, h, r, er, bb, so, w, l, sv, d, t, era)
    f.write("season_id, last, first, psid, team, g, gs, cg, ip, h, r, er, bb, so, w, l, sv, d, t, era\n")
    for season in season_list:
        print scrape_pitch_stats(season, f)
    f.close()

