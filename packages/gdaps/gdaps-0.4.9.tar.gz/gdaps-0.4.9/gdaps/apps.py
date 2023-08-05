import logging
import sys

from django.apps import AppConfig

from gdaps.pluginmanager import PluginManager
from gdaps import __version__

logger = logging.getLogger(__name__)


class GdapsPluginMeta:
    """This is the PluginMeta class of GDAPS itself."""

    version = __version__
    verbose_name = "Generic Django Application Plugin System"
    author = "Christian Gonzalez"
    author_email = "christian.gonzalez@nerdocs.at"
    category = "GDAPS"
    visible = False


class GdapsConfig(AppConfig):
    name = "gdaps"
    PluginMeta = GdapsPluginMeta

    def ready(self):
        # walk through all installed plugins and check some things
        for app in PluginManager.plugins():
            if hasattr(app.PluginMeta, "compatibility"):
                import pkg_resources

                try:
                    pkg_resources.require(app.PluginMeta.compatibility)
                except pkg_resources.VersionConflict as e:
                    logger.critical("Incompatible plugins found!")
                    logger.critical(
                        f"Plugin {app.name} requires you to have {e.req}, but you installed {e.dist}."
                    )

                    sys.exit(1)

        # load all gdaps.plugins - they must be implementations of GDAPS Interfaces
        logger.info("Loading gdaps plugins...")
        from pkg_resources import iter_entry_points

        for entry_point in iter_entry_points(group="gdaps.plugins", name=None):
            # it is enough to have them instantiated, as they are remembered internally in their interface.
            entry_point.load()
