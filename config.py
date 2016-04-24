try:
    import urllib.request as urllib_request #for python 3
except ImportError:
    import urllib2 as urllib_request # for python 2

import os
import os.path
import json
import threading
import time


class Config:

    DEFAULT_CONFIG_FILE = 'default_config.json'
    CONFIG_FILE = 'config.json'
    CONFIG_URL = 'https://raw.githubusercontent.com/aausat/aausat4_beacon_parser/master/default_config.json'
    UPDATE_FREQUENCY_MINUTES = 30

    def __init__(self):
        self.config_lock = threading.Lock()
        self.config = None
        self.load_config()
        self.update_config()

    def get_config(self):
        with self.config_lock:
            return self.config.copy()

    def load_config(self, only_if_new=False):
        # Load config file
        config_file = Config.CONFIG_FILE
        if not os.path.isfile(config_file):
            config_file = Config.DEFAULT_CONFIG_FILE
            if not os.path.isfile(config_file):
                # No config files
                return
        with open(config_file, 'r') as f:
            new_config = json.load(f)
            self.set_config(new_config, only_if_new)

    def set_config(self, config_dict, only_if_new):
        if not self.verify_config(config_dict):
            # Not valid
            return
        with self.config_lock:
            update = True
            if only_if_new and self.config != None:
                if self.config['version'] >= config_dict['version']:
                    update = False
                else:
                    print("Config updated (version {}).".format(config_dict['version']))
            if update:
                self.config = config_dict
            else:
                print("No need to update.")
            

    def update_config(self):
        print("Updating config...")
        try:
            f = urllib_request.urlopen(Config.CONFIG_URL)
            content = f.read()
            with open(Config.CONFIG_FILE, 'w') as f:
                f.write(content)
            config = json.loads(content)
            self.set_config(config, True)
        except Exception as e:
            print("Error: {}".format(e))
        # Start update config timer
        t = threading.Timer(60*Config.UPDATE_FREQUENCY_MINUTES, self.update_config, ())
        t.daemon=True
        t.start()
        
    def verify_config(self, config):
        valid = all(key in config for key in
                    ('version', 'tle', 'radio_settings'))
        if valid:
            return all(key in config['radio_settings'] for key in
                       ('bitrate', 'power', 'training', 'frequency', 'modindex'))
        return False
    
