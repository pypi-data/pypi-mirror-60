from django.apps import AppConfig, apps

import gdaps
from gdaps.apps import GdapsConfig


class FrontendPluginMeta:
    version = gdaps.__version__
    visible = False
    author = GdapsConfig.PluginMeta.author
    email = GdapsConfig.PluginMeta.author_email
    category = GdapsConfig.PluginMeta.category


class FrontendConfig(AppConfig):
    name = "gdaps.frontend"
    label = "gdaps_frontend"
    verbose_name = "GDAPS frontend"

    PluginMeta = FrontendPluginMeta

    def ready(self):
        pass
