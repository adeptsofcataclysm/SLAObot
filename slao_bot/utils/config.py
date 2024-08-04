import configparser

base_config = configparser.ConfigParser()
base_config.read('config/base.cfg')

guild_config = configparser.ConfigParser()
guild_config.read('config/guild.cfg')

default_config = {'SIGNUP_ENABLED': False,
                  'SIGNUP_CHANNEL': 0,
                  'WELCOME_MESSAGE': 'Welcome to guild server. Use /signup command if you want to join our guild!',
                  'EPGP_ENABLED': False,
                  'EPGP_UPLOAD_CHANNEL': 0,
                  }
