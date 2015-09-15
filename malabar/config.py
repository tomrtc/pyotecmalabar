import configparser
import click
import os

CONFIGURATION_APPLICATION_PATH = click.get_app_dir('malabar')
CONFIGURATION_FILE_NAME        = os.path.join(CONFIGURATION_APPLICATION_PATH, 'configuration.ini')
DEFAULT_GROUP                  ='otec'

RSS_DATABASE_FILE_PATH         = os.path.join(CONFIGURATION_APPLICATION_PATH, 'rss.db')
OTEC_TEMPLATE_RSS_URI          = "http://cdafactory.pqa-collab.fr.alcatel-lucent.com/rss.php"

class OtecCfg:
        def __init__(self, sfile, _interpolation):
                self.configparser = configparser.ConfigParser(interpolation=_interpolation)
                self.configparser.read(sfile)

        def getDefaultSettings(self):
                return self.getSettings(DEFAULT_GROUP)

        def getSettings(self, group):
                return self.configparser[group]

def get_configuration(config_file_name, interpolation=configparser.BasicInterpolation()):
        return OtecCfg(config_file_name, interpolation)
