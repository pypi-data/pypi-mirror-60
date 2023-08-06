from cc_utils.__about__ import __title__, __version__
import os
from os import environ
import yaml

def hello():
    return 'hello from {title} version {version}'.format(title=__title__, version=__version__)


def load_config_yml(app):
    # for development use yaml file to set env variables to avoid 
    # having to rebuild container and allow for different options
    if os.getenv("CONFIG_FILE"):
        config_path = os.path.join(app.instance_path, os.environ["CONFIG_FILE"])
    else:
        return

    def ENV(name, value):
        environ[name] = value

    with open(config_path, 'r') as stream:
        try:
            cfg = yaml.load(stream, Loader=yaml.FullLoader)
            for name, value in cfg.items():
                app.logger.debug(name + ":" + str(value))
                ENV(name, str(value))
        except yaml.YAMLError as exc:
            app.logger.error('error loading config.yml\n{0}'.format(exc))