import bluebox, fec
import config, parser, tracker, ircreporter
import threading
import argparse
import time
import binascii
from datetime import datetime

class bb_frontend(threading.Thread):

    LOGFILE = "log.txt"
    
    def __init__(self, qth=None, config_file=None, enable_tracking=False, enable_auth=False):
        c = config.Config(config_file)
        self.qth = qth
        self.config = c.get_config()

        if not config_file:
            c.add_observer(self)
        
        self.enable_tracking = enable_tracking

        self.bb_lock = threading.Lock()
        with self.bb_lock:
            self.bluebox = bluebox.Bluebox()
            
        self.parser = parser.Parser()
        self.update(self.config)
        
        if self.enable_tracking:
            self.tle = '\n'.join(self.config['tle'])
            self.tracker = tracker.Tracker(self.qth, self.tle)

        self.enable_auth = enable_auth
        if self.enable_auth:
            self.irc_reporter = ircreporter.IRCReporter()

    def update(self, config):
        settings = config['radio_settings']
        with self.bb_lock:            
            self.center_freq = settings['frequency']
            self.bluebox.set_frequency(self.center_freq)
            time.sleep(0.01)
            self.bluebox.set_modindex(settings['modindex'])
            time.sleep(0.01)
            self.bluebox.set_bitrate(settings['bitrate'])
            time.sleep(0.01)
            self.bluebox.set_power(settings['power'])
            time.sleep(0.01)
            self.bluebox.set_training(settings['training'])
            time.sleep(0.01)
            self.bluebox.set_syncword(int(settings['syncword'], 16))
            time.sleep(0.01)
            
    def run(self):
        if self.enable_tracking:
            self.__run_pass__()
        else:
            self.__receive_mode__()

    def receive(self):
        with self.bb_lock:
            data, rssi, freq = self.bluebox.receive(50000)
        if data:
            print("\n" + "#="*40 + "#\n")
            print("Received packet {}".format(datetime.now().isoformat(' ')))
            print("{}\n".format(data))

            print binascii.b2a_hex(data)

            if self.enable_auth:
                hex_str = binascii.b2a_hex(data)
                print len(hex_str)
                self.irc_reporter.send("AUTH,1,%s" % hex_str[0:len(hex_str)/2])
                self.irc_reporter.send("AUTH,2,%s" % hex_str[len(hex_str)/2:])

            # Parse data
            try:
                beacon_str = self.parser.parse_data(data)
            except Exception as e:
                print e
            else:
                return beacon_str

    def __run_pass__(self):
        while True:
            while self.tracker.in_range():
                freq = self.config['radio_settings']['frequency'] + self.tracker.get_doppler()
                print "Doppler freq:", freq
                self.bluebox.set_frequency(freq)
                beacon = self.receive()
                if beacon:
                    print beacon
                
            next_pass, duration, max_elvation = self.tracker.next_pass()
            print """Next pass: {0}
Duration: {1:.0f} minutes
Max elevation: {2:.2f} degrees""".format(datetime.fromtimestamp(next_pass), duration / 60, max_elvation)

            time.sleep(next_pass-time.time())
            

    def __receive_mode__(self):
        while True:
            beacon = self.receive()
            if beacon:
                print beacon



if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='AAUSAT4 Bluebox based Beacon Parser')
    args_parser.add_argument('--lat', dest='lat', required=False, type=float, default=None,
                             help='Latitude of ground station (N), e.g. 55.6167')
    args_parser.add_argument('--lon', dest='lon', required=False, type=float, default=None,
                             help='Longitude of ground station (W), e.g. -12.6500')
    args_parser.add_argument('--alt', dest='alt', required=False, type=float, default=None,
                             help='Altitude of ground station (meters), e.g. 10')
    args_parser.add_argument('--disable-tracking', dest='disable_tracking',
                             action='store_true',
                             required=False, default=False,
                             help='Disables doppler correction and pass planning.')
    args_parser.add_argument('--enable-authentication', dest='enable_authentication',
                             action='store_true',
                             required=False,
                             help='Enables automatic reporting of received packets.')
    args_parser.add_argument('--config-file', dest='config_file', required=False, type=str, default=None,
                             help='Use a confguration file from the local disk instead of the one provided by AAUSAT (on github).')

    args = args_parser.parse_args()

    if args.disable_tracking:
        qth = None
    else:
        try:
            qth = (args.lat, args.lon, args.alt)
        except:
            raise Exception("latitude longitude and altitude arguments are required for tracking")

    bb = bb_frontend(qth, args.config_file, args.disable_tracking, args.enable_authentication)
    bb.run()
     
