from utils import plugins

PLUGIN_NAME = "downloads_by_country"
DISPLAY_NAME = "Downloads by Country"
DESCRIPTION = "A world map and table of article downloads and views by country."
AUTHOR = "Rod Library, University of Northern Iowa"
VERSION = "1.0"
SHORT_NAME = "downloads_by_country"
MANAGER_URL = "downloads_by_country_index"
JANEWAY_VERSION = "1.8.0"


class DownloadsByCountryPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME
    version = VERSION
    janeway_version = JANEWAY_VERSION
    manager_url = MANAGER_URL


def install():
    DownloadsByCountryPlugin.install()


def hook_registry():
    return {
        "additional_nav": {
            "module": "plugins.downloads_by_country.hooks",
            "function": "nav_hook",
        },
    }
