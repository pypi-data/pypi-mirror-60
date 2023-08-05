import logging
from pathlib import Path

from hed_utils.selenium import chrome_driver, SharedDriver
from hed_utils.support import log

from find_episodes import config, episodes

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def init_config():
    """Entry point for 'find-episodes-init' CLI hook"""

    print()
    print("Running 'find-episodes-init' in dir: %s", str(Path.cwd()))
    config.write_sample()


def find_episodes():
    """Entry point for 'find-episodes' CLI hook"""

    print("Running 'find-episodes' in dir: ", str(Path.cwd()))

    cfg = config.load_config()
    if cfg.logging_enabled:
        log.init(level=logging.INFO)

    _log.info("Starting chromedriver in headless mode...")
    driver = chrome_driver.create_instance(headless=True)
    SharedDriver.set_instance(driver)

    results = episodes.find(cfg.in_site,
                            cfg.from_episode,
                            cfg.to_episode,
                            cfg.search_template)

    output = episodes.prettify(results)
    print("Matching episodes:")
    print(output)

    file = Path.cwd().joinpath("episodes.txt")
    file.write_text(output, encoding="utf-8")
    print("Saved output to: ", str(file))
