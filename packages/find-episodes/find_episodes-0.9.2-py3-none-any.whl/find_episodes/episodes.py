import logging
from operator import itemgetter
from typing import List, Tuple

from hed_utils.selenium import FindBy, SharedDriver
from selenium.webdriver.common.keys import Keys
from tabulate import tabulate

driver = SharedDriver()

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class Google:
    SEARCH_RESULTS = FindBy.CSS_SELECTOR("div#search div#rso div.r > a:nth-child(1)", required=False)
    SEARCH_INPUT = FindBy.CSS_SELECTOR("input[name='q']")

    @staticmethod
    def go_to():
        _log.info("Navigating to Google")
        driver.get("https://www.google.com")

    @classmethod
    def search_for(cls, query):
        _log.info(f"Searching for: '%s'", query)
        cls.SEARCH_INPUT.clear()
        cls.SEARCH_INPUT.send_keys(query + Keys.ENTER)
        driver.wait_for_page_load()

    @classmethod
    def get_visible_results(cls):
        return [(result.find_element_by_xpath("./h3").text, result.get_attribute("href"))
                for result
                in cls.SEARCH_RESULTS]


def find(in_site: str, from_episode: int, to_episode: int, search_template: str):
    _log.info("Searching for episodes: in_site='%s', from_episode=%s, to_episode=%s, search_template='%s'",
              in_site, from_episode, to_episode, search_template)

    episodes = set()

    Google.go_to()
    for current_ep in range(from_episode, to_episode):
        query = search_template.format(episode=current_ep)
        Google.search_for(query)

        for title, url in Google.get_visible_results():
            if (query in title) and (in_site in url):
                episodes.add((title, url))

    _log.info("Got %s matching episodes!", len(episodes))
    return list(sorted(episodes, key=itemgetter(0)))


def prettify(results: List[Tuple[str, str]]):
    return tabulate(tabular_data=results,
                    headers=["TITLE", "URL"],
                    tablefmt="fancy_grid")
