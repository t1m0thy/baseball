import mechanize
import os
import logging
import gzip

logger = logging.getLogger("scrapetools")


def ungzipResponse(r, br):
    headers = r.info()
    if headers['Content-Encoding'] == 'gzip':
        gz = gzip.GzipFile(fileobj=r, mode='rb')
        html = gz.read()
        gz.close()
        headers["Content-type"] = "text/html; charset=utf-8"
        r.set_data(html)
        br.set_response(r)


def get_cached_url(url, cache_filename=None, force_reload=False):
    if force_reload or cache_filename is None or not os.path.isfile(cache_filename):
        logging.info("getting page at " + url)
        br = mechanize.Browser()
        # Browser options
        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT6.0; en-US; rv:1.9.0.6')]
        br.addheaders.append(('Accept-Encoding', 'gzip'))

        br.open(url)
        response = br.response()
        ungzipResponse(response, br)
        html = response.read()

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
