from deluge.plugins.pluginbase import WebPluginBase
from .common import MODULE_NAME, get_resource
WEBUI_SCRIPT = "%s.js" % MODULE_NAME


class WebUI(WebPluginBase):
    scripts = [get_resource(WEBUI_SCRIPT)]
    debug_scripts = scripts
