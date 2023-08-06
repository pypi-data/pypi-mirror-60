from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from .libraries.SimpleAuthServer import serve_http
from .libraries.Zipping import create_archive
import os
import socket
try:
    import _thread as thread  # Python 3
except ImportError:
    import thread  # Python 2

# Would be nice to log some events for debugging purpose
# from deluge.log import LOG as log
# htttp and socket would be better implemented using directly twisted
# from twisted.internet.task import LoopingCall

DEFAULT_ARCHIVE_NAME = 'deluge_archive.zip'  # Needs to be a url friendly name
DEFAULT_PREFS = {
    "http_username": "deluge",
    "http_password": "deluge",
    "http_port": 8007,
    "http_hostname": None  # Will be overriden in the enable function
}


class Core(CorePluginBase):
    def enable(self):
        http_hostname_default = socket.getfqdn()
        DEFAULT_PREFS['http_hostname'] = http_hostname_default
        self.config = deluge.configmanager.ConfigManager("delugewebbrowser.conf", DEFAULT_PREFS)
        self.http_port = self.config["http_port"]
        self.http_username = self.config["http_username"]
        self.http_password = self.config["http_password"]
        self.http_hostname = self.config["http_hostname"]
        # Todo: Would be better to use directly twisted!
        thread.start_new_thread(self.start_server_static, ())
        # Not sure following line is needed
        self.config.save()

    def disable(self):
        self.config["http_port"] = self.http_port
        self.config["http_username"] = self.http_username
        self.config["http_password"] = self.http_password
        self.config["http_hostname"] = self.http_hostname
        # Not sure following line is needed
        self.config.save()
        # Todo: close cleanely the started new thread.

    def update(self):
        pass

    @export
    def set_config(self, config):
        "sets the config dictionary"
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        "returns the config dictionary"
        # Todo: use this in the frontend to parametrise the config
        return self.config.config

    @export
    def get_base_url(self):
        return "http://{}:{}@{}:{}".format(self.http_username, self.http_password, self.http_hostname, self.http_port)

    @export
    def get_zip_url(self, save_path, name):  # need to check calls to files or path
        path = os.path.join(save_path, name)
        create_archive(path, DEFAULT_ARCHIVE_NAME)
        return "{}/{}".format(self.get_base_url(), DEFAULT_ARCHIVE_NAME)

    def start_server_static(self):
        directory = component.get("Core").get_config_value('download_location')
        serve_http(username=self.http_username,
                   password=self.http_password,
                   port=self.http_port,
                   directory=directory)
