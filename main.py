"""
Sublack

Order of imports should not be changed
"""
# standard library
import logging
import os

# pypi/conda library
import sublime

from .sublack import (  # flake8: noqa
    PACKAGE_NAME,
    SETTINGS_FILE_NAME,
    BlackDiffCommand,
    BlackdStartCommand,
    BlackdStopCommand,
    BlackEventListener,
    BlackFileCommand,
    BlackFormatAllCommand,
    BlackToggleBlackOnSaveCommand,
    Path,
    cache_path,
    clear_cache,
    get_settings,
)

LOG = logging.getLogger(PACKAGE_NAME)

if not os.environ.get("CI", None):
    LOG.propagate = False


def plugin_loaded():
    # load config
    current_view = sublime.active_window().active_view()
    config = get_settings(current_view)
    if config["black_log"] == None:
        config["black_log"] = "info"
    # Setup  logging
    if not LOG.handlers:
        debug_formatter = logging.Formatter("[{}:%(filename)s](%(levelname)s) %(message)s".format(PACKAGE_NAME))
        dh = logging.StreamHandler()
        dh.setLevel(logging.DEBUG)
        dh.setFormatter(debug_formatter)
        LOG.addHandler(dh)

    try:
        LOG.setLevel(config.get("black_log").upper())
    except ValueError as err:  # https://forum.sublimetext.com/t/an-odd-problem-about-sublime-load-settings/30335/6
        LOG.error(err)
        LOG.setLevel("ERROR")
        LOG.error("fallback to loglevel ERROR")

    LOG.info("Loglevel set to %s", config["black_log"].upper())

    # check cache_path
    cp = cache_path()
    if not cp.exists():
        cp.mkdir()

    # clear cache
    clear_cache()

    # # check blackd autostart
    if config["black_blackd_autostart"]:
        sublime.set_timeout_async(lambda: current_view.run_command("blackd_start"), 0)

    # watch for loglevel change
    sublime.load_settings(SETTINGS_FILE_NAME).add_on_change("black_log", lambda: Path(__file__).touch())
