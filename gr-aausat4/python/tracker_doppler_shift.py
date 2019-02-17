#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2019 Nick Oestergaard.
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
import pmt
from gnuradio import gr
import tracker
import time
import dateutil.parser as dateparser



from threading import Thread


class tracker_doppler_shift(gr.sync_block):
    """
    docstring for block tracker_doppler_shift
    """
    def __init__(self, tle_title, tle_1, tle_2, comm_freq_tx, comm_freq_rx, gs_lon, gs_lat, gs_alt, obs_start, obs_end, time_resolution_us):
        gr.sync_block.__init__(self,
            name="tracker_doppler_shift",
            in_sig=[],
            out_sig=[])

        tle = "{}\n{}\n{}".format(tle_title, tle_1, tle_2)
        print("lat: {}, lon: {}".format(gs_lat, -gs_lon))
        qth = (gs_lat, -gs_lon, gs_alt)
        self.time_resolution_us = time_resolution_us
        
        a = dateparser.parse(obs_start)
        b = dateparser.parse(obs_end)
        self.obs_start = time.mktime(a.timetuple()) + a.microsecond / 1E6
        self.obs_end = time.mktime(b.timetuple()) + b.microsecond / 1E6
        print(obs_start)
        print(obs_end)
        print(self.obs_start)
        print(self.obs_end)
        print(self.obs_end - self.obs_start)
        print(tle)

        self.d_obs_elapsed = self.obs_start

        print(qth)
        print(tle)
        print(comm_freq_tx)
        self.mytracker = tracker.Tracker(qth, tle, comm_freq_tx )
        self.mytracker.set_center_frequncy(comm_freq_tx)
        self.comm_freq_tx = comm_freq_tx


        print(self.mytracker.get_doppler(obs_time=self.obs_start))
        print(self.mytracker.get_doppler(obs_time=self.obs_end))

        self.message_port_register_out(pmt.intern('doppler_out'))

        self.thread = Thread(target = self.mything, args = (4, ))
        #self.thread.daemon = True

        '''
        tle = """AAUSAT-II
1 32788U 08021F   16109.53422999  .00001855  00000-0  18309-3 0  9992
2 32788  97.6100 154.3596 0013832 108.1455 252.1273 14.93074504432296"""
        qth = (55.6167, -12.6500, 5) # lat (N), long (W), alt (meters)
        '''
        tle = """AAUSAT 4 468423
1 41460U 16025E   19045.15536849  .00002046  00000-0  10670-3 0  9998
2 41460  98.1056 126.3653 0160243  50.8229 310.7106 15.06807639153916"""
        qth = (57.014, -9.986, 10) 


        a = dateparser.parse("2019-02-14 13:09:35.000")
        b = dateparser.parse("2019-02-14 13:15:23.000")
        obs_start = time.mktime(a.timetuple()) + a.microsecond / 1E6
        obs_end = time.mktime(b.timetuple()) + b.microsecond / 1E6
        d_obs_elapsed = obs_start

        while d_obs_elapsed <= obs_end:
            atracker = tracker.Tracker(qth, tle, 437.424e6)
            
            print("TIME: {}".format(d_obs_elapsed))
            print atracker.in_range(obs_time=d_obs_elapsed)
            #print atracker.next_pass()
            print("Az: {} El: {}".format(atracker.get_azimuth(obs_time=d_obs_elapsed), atracker.get_elevation(obs_time=d_obs_elapsed)))
            print atracker.get_doppler(obs_time=d_obs_elapsed)
            d_obs_elapsed = d_obs_elapsed + 100

        print("Pass length was: {} seconds".format(d_obs_elapsed-obs_start))


        self.thread.start()

        #self.thread.join()


    def mything(self, iterations):

        while True:
            doppler = float(self.comm_freq_tx ) + self.mytracker.get_doppler(obs_time=self.d_obs_elapsed)
            print("Doppler: {} @ {} s".format(doppler, self.d_obs_elapsed))
            print("In range: {}".format(self.mytracker.in_range(obs_time=self.d_obs_elapsed)))
            self.message_port_pub(pmt.intern('doppler_out'), pmt.from_double(doppler))
            time.sleep(self.time_resolution_us/1000000)
            self.d_obs_elapsed = self.d_obs_elapsed + float(self.time_resolution_us/1000000)


