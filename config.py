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

    CONFIG_URL = 'https://raw.githubusercontent.com/aausat/aausat4_beacon_parser/master/default_config.json'
    UPDATE_FREQUENCY_MINUTES = 30

    def __init__(self, config_file=None):
        self.config_lock = threading.Lock()
        self.config = None
        self.observers = []

        if config_file:
            with open(config_file, 'r') as conf_file:
                conf = json.loads(conf_file.read())
                self.confif = self.set_config(conf, False)
        else:
            self.__auto_update_config__()
            
    def add_observer(self, observer):
        self.observers.append(observer)

    def delete_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(obersver)

    def notify_observers(self, config=None):
        for observer in self.observers:
            observer.update(config)
            
    def get_config(self):
        with self.config_lock:
            return self.config.copy()

    def set_config(self, config_dict, only_if_new):
        if not self.verify_config(config_dict):
            raise Exception("Invalid config")

        with self.config_lock:
            update = True
            if only_if_new and self.config != None:
                if self.config['version'] >= config_dict['version']:
                    update = False
                else:
                    print("Config updated (version {}).".format(config_dict['version']))
            if update:
                self.config = config_dict
                self.notify_observers(self.config)
            else:
                print("No need to update.")

    def __auto_update_config__(self):
        print("Updating config...")
        try:
            f = urllib_request.urlopen(Config.CONFIG_URL)
            content = f.read()
            config = json.loads(content)
            self.set_config(config, True)
        except Exception as e:
            print("Error: {}".format(e))
        # Start update config timer
        print("Config is up to date")
        t = threading.Timer(60*Config.UPDATE_FREQUENCY_MINUTES, self.__auto_update_config__, ())
        t.daemon=True
        t.start()
        
    def verify_config(self, config):
        valid = all(key in config for key in
                    ('version', 'tle', 'radio_settings'))
        if valid:
            return all(key in config['radio_settings'] for key in
                       ('bitrate', 'power', 'training', 'frequency', 'modindex'))
        return False
    
if __name__ == '__main__':
    class TestConfig:
        def __init__(self):
            c = Config()
            c.get_config()
            c.add_observer(self)
            
        def update(self, config):
            print config
    
    tc = TestConfig()
