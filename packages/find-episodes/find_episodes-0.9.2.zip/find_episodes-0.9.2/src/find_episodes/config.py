import logging
from collections import namedtuple
from configparser import ConfigParser
from pathlib import Path

from hed_utils.support import config_tool

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

FILE_NAME = "find-episodes.ini"

SECTION_NAME = "search-config"

DEFAULTS = dict(logging_enabled="yes",
                in_site="www.anime-planet.com",
                from_episode="100",
                to_episode="110",
                search_template="Watch Gintama Episode {episode} Online")

SearchConfig = namedtuple("SearchConfig", "logging_enabled in_site from_episode to_episode search_template")


def write_sample():
    """Writes sample find-episodes.ini in the current working dir"""

    dst_file = str(Path.cwd().joinpath(FILE_NAME).absolute())
    cfg = ConfigParser()
    cfg[SECTION_NAME] = DEFAULTS.copy()
    config_tool.write_config(cfg, dst_file)
    print("Created sample config file at: %s" % str(dst_file))
    print("Edit the values and run 'find-episodes' to perform the search.")


def load_config() -> SearchConfig:
    src_file = str(Path.cwd().joinpath(FILE_NAME))
    parser = config_tool.parse_file(src_file)
    print(f"loaded config:\n{config_tool.format_parser(parser)}")
    return SearchConfig(parser.getboolean(SECTION_NAME, "logging_enabled"),
                        parser.get(SECTION_NAME, "in_site"),
                        parser.getint(SECTION_NAME, "from_episode"),
                        parser.getint(SECTION_NAME, "to_episode"),
                        parser.get(SECTION_NAME, "search_template"))
