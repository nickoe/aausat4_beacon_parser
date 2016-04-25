#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# 
# Copyright 2016 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

from collections import deque
import binascii


import sys
sys.path.append("..")
import config, parser

class beacon_parser(gr.sync_block):
    """
    docstring for block beacon_parser
    Expecting an unpacked byte stream as input (one byte per bit LSB)
    """
    def __init__(self, packet_len):
        gr.sync_block.__init__(self,
            name="beacon_parser",
            in_sig=[numpy.byte],
            out_sig=None)
        self.stream = deque(maxlen=packet_len+8)
        self.packet_len = packet_len
        self.size = 0
        self.offset = 0
        self.tagged_index = 0
        self.packet  = 0



    #def work(self, input_items, output_items):
    #    in0 = input_items[0]
    #    # <+signal processing here+>
    #    return len(input_items[0])


    def work(self, input_items, output_items):
        in0 = input_items[0]
        nread = self.nitems_read(0) #number of items read on port 0
        ninput_items = len(input_items[0])

        #read all tags associated with port 0 for items in this work function
        tags = self.get_tags_in_range(0, nread, nread+ninput_items)

        #work stuff here...
        #when tag is present
        #find self.offset in input_items
        #gueue from that self.offset untill packet length has been reached
        # 0x59 (89d) 0x8C (140d)
        # 01011001 10001100
        if tags != ():
            print tags

            for item in tags:
                print(item.key)
                print(item.offset)
                self.offset = item.offset
                print(item.value)

            print input_items[0]
            print "nread = ", nread
            print "ninput_items = ", ninput_items
            self.tagged_index = self.offset-nread
            print "self.tagged_index = ", self.tagged_index
            print "self.offset = ", self.offset
            print "tag loop", self.stream

            print "size = ", self.size
            self.size = 0
            self.packet = 1

            # Reference data sanity check
            s = ' '
            for i in xrange(self.tagged_index*2):
                s += ' '
            print s[:-1], "0 1 0 1 1 0 0 1 1 0 0 0 1 1 0 0"
            s += '. - - - - - - . . - - - - - - .'
            print s
            print in0
        
        else:
            self.size = len(self.stream) + ninput_items
            self.tagged_index = 0 # we are in the following bytes
            #print "in0=", in0[self.tagged_index:self.packet_len-self.size]
        if self.packet == 1:
            #print "######"
            #print ninput_items
            self.stream.extend(in0[self.tagged_index:self.tagged_index+self.packet_len-self.size])

        if len(self.stream) == self.packet_len:
            print "Queue is full: "#, self.stream
            bindata = []
            while len(self.stream) != 0:
                bindata += [self.stream.popleft()]

            bit_str = ''.join([str(b) for b in bindata])
            hexdata = hex(int(bit_str,2))
            print "hexdata=",hexdata
            print "hexdata=",hexdata[4:-1]

            psr = parser.Parser()
            try:
                a = psr.parse_data(binascii.a2b_hex(hexdata[4:-1]))
                print a
            except:
                print "Decoding error"
            # reset to empty
            self.stream.clear()
            self.packet = 0
        

        return len(input_items[0])

    def worktest(self,in0, ninput_items):
        self.stream.extend(in0)

    def test(self):
        print "It Works!"
        self.tagged_index = 2
        testvector = "abcdefghijklmnopqrstuvxyz"
        self.worktest(testvector[0:2],2)
        self.worktest(testvector[2:4],2)
        self.worktest(testvector[4:6],2)
        self.worktest(testvector[6:10],4)
        self.worktest(testvector[10:12],2)
        self.worktest(testvector[12:14],2)
        self.worktest(testvector[14:16],2)



if __name__ == '__main__':
    a = beacon_parser(24)
    a.test()
