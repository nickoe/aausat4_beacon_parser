import bluebox, fec, predict
import beacon, config
import binascii, struct
import time, aenum, threading
import argparse
from datetime import datetime

class CSP_adress(aenum.Enum):
    ESP   = 0
    FP    = 1
    LOG   = 1
    SWISS = 1
    AIS2  = 3
    UHF   = 4
    ADCS1 = 5
    ADCS2 = 6
    MCC   = 9

class Parser():
    
    def __init__(self, verify_packets=False):
        self.verify_packets = verify_packets
        self.ec = fec.PacketHandler()

        
    def verify_packet(self, packet):
        pass
    
    def parse_data(self, bin_data):
        data, bit_corr, byte_corr = self.ec.deframe(bin_data)
        
        payload = None
        if self.verify_packets:
            resp = self.verify_packet(bin_data)
            # print resp['status'] - something linke: payload data from ss to ss
            #                                       : failed verification 
            #                                       : beacon packet
            # if beacon, extract payload

        else:
            # Parsing with verification
            hexdata = binascii.b2a_hex(data)
            print hexdata
            header = struct.unpack("<I", data[0:4])[0]
            # Parse CSP header
            src = ((header >> 25) & 0x1f)
            dest = ((header >> 20) & 0x1f)
            dest_port = ((header >> 14) & 0x3f)
            src_port = ((header >> 8) & 0x3f)
            if CSP_adress(src) == CSP_adress.UHF and CSP_adress(dest) == CSP_adress.MCC and dest_port == 10:
                payload = hexdata[8:-4]
            else:
                raise Exception("Possibly payload data from {0} to {1}. Will not attempt to parse".format(CSP_adress(src), CSP_adress(dest)))
        
        if payload:
            beacon_decode = beacon.Beacon(payload)
            return str(beacon_decode)
