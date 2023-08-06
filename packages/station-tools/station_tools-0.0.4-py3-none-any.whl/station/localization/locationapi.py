import logging
import utm
import pandas as pd

from station.localization import dataset

class LocationApi:
    """utility for localizing tags in merged beep/node dataset"""
    def __init__(self, beep_filename, node_filename):
        """filenames of raw beep data and node location data"""
        self.beeps = dataset.BeepLocationDataset(beep_filename, node_filename) 

    def weighted_average(self, freq):
        """generate weighted average location dataset"""
        return self.beeps.df.resample(freq).mean()

if __name__ == '__main__':
    import sys
    loc = LocationApi(
        beep_filename='~/data/lifetag/archbold/archbold-calibration-test.csv',
        node_filename='~/data/lifetag/archbold/archbold-nodes.csv'
    )
    print(loc.df)