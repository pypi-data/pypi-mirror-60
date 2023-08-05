import subprocess

from gdaps.api import Interface
from gdaps import __version__


@Interface
class IPackageManager:
    """Interface for package manager representation."""

    name = None

    def _exec(self, command: str, cwd: str):
        """Convenience function for implementers to exec a command in the shell."""
        subprocess.check_call(command, cwd=cwd, shell=True)

    def init(self, cwd, version=__version__, description="", license=None) -> None:
        """The init command to create a repository."""
        raise NotImplementedError

    def install(self, pkg, cwd):
        """The command to install a package. use '{pkg}' as replacement for the package."""
        raise NotImplementedError

    def installglobal(self, pkg, cwd):
        """The command to install a package globally. use '{pkg}' as replacement for the package."""
        raise NotImplementedError

    def uninstall(self, pkg, cwd):
        """The command to uninstall a package"""
        raise NotImplementedError


@Interface
class IFrontendEngine:
    # FrontendEngines should not be instantiated.
    __service__ = False

    """The name of the frontend which can be used by GDAPS, e.g. 'vue', 'react', etc."""
    name = None

    """A list of tuples for template file endings that should be renamed and rendered as templates."""
    rewrite_template_suffixes = ()  # e.g. (".js-tpl", ".js")

    """A list of (relative) file names that also be treated as templates."""
    extra_files = []

    extensions = ()

    """A list of package managers that are supported by this engine"""
    package_managers = []

    __package_manager = None

    """Global/plugin template paths that this engine provides."""
    template_global = None
    template_plugin = None

    @classmethod
    def check_prereq(cls):
        """Checks for prerequisites.

        This method should check if system commands and libraries that are needed for this engine are available.
        An easy check for commands within PATH is shutil.which()."""

    @classmethod
    def initialize(cls, frontend_dir: str):
        """Initializes engine.

        This method is called when the frontend is created, and will be only called once.
        It should install all frontend specific stuff, e.g. using Js libraries using 'yarn/npm install' etc.
        It can assume that the BASE_DIR/frontend_dir/ exists, and uses the package manager
        defined in settings.FRONTEND_PKG_MANAGER.
        :param frontend_dir: relative directory within BASE_DIR where the frontend lives.
        """

    @staticmethod
    def update_plugins_list() -> None:
        """Updates a list of plugins that the frontend can include dynamically then.

        This can be different from frontend to frontend. Easiest way is to create a Javascript
        module that exports an [array] of paths that point to modules that e.g. webpack then imports.
        :param plugin_paths: a list of module names that contain a frontend directory with a Javascript module.
        """
        # TODO: rename to syncplugins
