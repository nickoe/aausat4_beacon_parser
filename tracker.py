import predict
import time
import dateutil.parser as dateparser

class Tracker:

    def __init__(self, qth, tle, center_freq):
        self.qth = qth
        self.tle = tle
        self.freq = center_freq

    def set_center_frequncy(self, center_freq):
        self.freq = center_freq

    def get_doppler(self, obs_time=None):
        if not obs_time:
            obs_time = time.time()
        prediction = predict.observe(self.tle, self.qth, obs_time)
        doppler = prediction['doppler']
        correction = (self.freq/100E6) * doppler
        return correction

    def in_range(self, obs_time=None):
        if not obs_time:
            obs_time = time.time()

        if self.get_elevation(obs_time) > 0:
            return True
        else:
            return False

    def next_pass(self, obs_time=None):
        if not obs_time:
            obs_time = time.time()

        p = predict.transits(self.tle, self.qth, ending_after=obs_time)
        transit = p.next()
        return transit.start, transit.duration(), transit.peak()['elevation']

    def get_elevation(self, obs_time=None):
        if not obs_time:
            obs_time = time.time()

        prediction = predict.observe(self.tle, self.qth, obs_time)
        return prediction['elevation']

    def get_azimuth(self, obs_time=None):
        if not obs_time:
            obs_time = time.time()

        prediction = predict.observe(self.tle, self.qth, obs_time)
        return prediction['azimuth']

if __name__ == '__main__':
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
        tracker = Tracker(qth, tle, 437.424e6)
        
        print("TIME: {}".format(d_obs_elapsed))
        print tracker.in_range(obs_time=d_obs_elapsed)
        #print tracker.next_pass()
        print("Az: {} El: {}".format(tracker.get_azimuth(obs_time=d_obs_elapsed), tracker.get_elevation(obs_time=d_obs_elapsed)))
        print tracker.get_doppler(obs_time=d_obs_elapsed)
        d_obs_elapsed = d_obs_elapsed + 100

    print("Pass length was: {} seconds".format(d_obs_elapsed-obs_start))
