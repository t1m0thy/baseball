import mechanize
import os
import logging

logger = logging.getLogger("scrapetools")


def get_cached_url(url, cache_filename=None, force_reload=False):
    if force_reload or cache_filename is None or not os.path.isfile(cache_filename):
        logging.info("getting game at " + url)
        br = mechanize.Browser()
        # Browser options
        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT6.0; en-US; rv:1.9.0.6')]
        br.open(url)
        html = br.response().read()

        if cache_filename is not None:
            f = open(cache_filename, 'aw')
            f.write(html)
            f.close()
        else:
            return html
    return open(cache_filename, 'r').read()


class RawEvent:
    def is_sub(self):
        raise NotImplementedError

    def batter(self):
        raise NotImplementedError

    def title(self):
        raise NotImplementedError

    def text(self):
        raise NotImplementedError


class HalfInning:
    def raw_events(self):
        """
        iterator that returns RawEvents
        """
        raise NotImplementedError


class GameScraper:

    def home_team(self):
        raise NotImplementedError

    def away_team(self):
        raise NotImplementedError

    def halfs(self):
        raise NotImplementedError
