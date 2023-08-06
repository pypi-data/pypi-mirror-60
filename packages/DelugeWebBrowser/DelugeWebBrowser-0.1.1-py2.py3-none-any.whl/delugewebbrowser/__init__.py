from deluge.plugins.init import PluginInitBase
__author__ = "Hicham Tahiri"
__email__ = "aerospeace+dev@gmail.com"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.1.1"

class CorePlugin(PluginInitBase):
  def __init__(self, plugin_name):
    # from .core.core import Core as _plugin_cls
    from .core import Core as _plugin_cls
    self._plugin_cls = _plugin_cls
    super(CorePlugin, self).__init__(plugin_name)


class GtkUIPlugin(PluginInitBase):
  def __init__(self, plugin_name):
    # from .gtkui.gtkui import GtkUI as _plugin_cls
    from .gtkui import GtkUI as _plugin_cls
    self._plugin_cls = _plugin_cls
    super(GtkUIPlugin, self).__init__(plugin_name)


class WebUIPlugin(PluginInitBase):
  def __init__(self, plugin_name):
    from .webui import WebUI as _plugin_cls
    self._plugin_cls = _plugin_cls
    super(WebUIPlugin, self).__init__(plugin_name)
