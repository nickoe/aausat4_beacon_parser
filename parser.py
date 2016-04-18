import bluebox
import fec
import binascii
import time
import struct
import beacon
import config
import threading

class Parser(threading.Thread):

    DEFAULT_FREQUENCY = 437425000
    DEFAULT_MODINDEX = 1
    DEFAULT_BITRATE = 2400
    DEFAULT_POWER = 26
    DEFAULT_TRAINING = 200
    
    def __init__(self, qth, config, enable_doppler=True):
        self.qth = qth
        self.center_freq = Parser.DEFAULT_FREQUENCY
        self.bb_lock = threading.Lock()
        with self.bb_lock:
            self.bluebox = bluebox.Bluebox()

        self.config_version = -1            
        self.set_config(config, True)

    def set_config(self, config, force_update=False):
        with self.bb_lock:
        if config:
            if force_update or ('version' in config and config['version'] > self.config_version):
                settings = config['radio_settings']
                self.center_freq = settings['frequency'] if 'frequency' in settings else DEFAULT_FREQUENCY

                self.bluebox.set_frequency(self.center_freq)
                time.sleep(0.01)
                self.bluebox.set_modindex(settings['modindex']) if 'modindex' in settings else None
                time.sleep(0.01)
                self.bluebox.set_bitrate(settings['bitrate']) if 'bitrate' in settings else None
                time.sleep(0.01)
                self.bluebox.set_power(settings['power']) if 'power' in settings else None
                time.sleep(0.01)
                self.bluebox.set_training(settings['training']) if 'training' in settings else None
                self.config_version = config['version'] if 'version' in config else self.config_version
                
            elif force_update:
                # Set default config
                self.bluebox.set_frequency(Parser.DEFAULT_FREQUENCY)
                time.sleep(0.01)
                self.bluebox.set_modindex(Parser.DEFAULT_MODINDEX)
                time.sleep(0.01)
                self.bluebox.set_bitrate(Parser.DEFAULT_BITRATE)
                time.sleep(0.01)
                self.bluebox.set_power(Parser.DEFAULT_POWER)
                time.sleep(0.01)
                self.bluebox.set_training(Parser.DEFAULT_TRAINING)
            

    def run(self):
        while True:
            try:
                with self.bb_lock:
                    data, rssi, freq = self.bluebox.receive(1000)
                if data:
                    # Parse data
                    packet = self.parse_data(data)
                    # TODO: Report
            except Exception as e:
                print e
            # Update config if updated
            # An observer might be more useful
            config = self.config.get_config()
            self.set_config(config)


    def __enable_doppler_correction__(self):
        def doppler_correction(self):
            # the predict library expects long (W)
            # We expect long (E)
            qth = self.qth
            qth[1] = -qth[1]
            
            sat_info = predict.observe(tle, , time)

            with self.bb_lock:
                self.bluebox.set_frequency(self.center_freq + sat_info['doppler'])

        threading.Timer(1, doppler_correction, ()).start()

            
        
    
    def parse_data(self, data):
        # FEC
        ec = fec.PacketHandler()
        data, bit_corr, byte_corr = ec.deframe(data)
        # 
        header = struct.unpack("<I", data[0:4])[0]

        # Wrong idianess - check mcc server (csp_if_bb)
        data = binascii.b2a_hex(data)
        payload = data[8:-4]

        # Parse CSP header
        src = ((header >> 25) & 0x1f)
        dest = ((header >> 20) & 0x1f)
        dest_port = ((header >> 14) & 0x3f)
        src_port = ((header >> 8) & 0x3f)

        print(src)
        print(dest)
        print(dest_port)
        print(src_port)
        print(payload)

        print(len(payload))
        b = beacon.Beacon(payload)
        print b
        
if __name__ == '__main__':
    config = config.Config()
    parser = Parser(config)
    parser.parser_loop()
