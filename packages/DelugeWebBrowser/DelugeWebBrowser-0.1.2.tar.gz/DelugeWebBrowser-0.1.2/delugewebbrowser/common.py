MODULE_NAME = 'delugewebbrowser'


def get_resource(filename):
    import pkg_resources
    import os
    return pkg_resources.resource_filename(MODULE_NAME, os.path.join("data", filename))
