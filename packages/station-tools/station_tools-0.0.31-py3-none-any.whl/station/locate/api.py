import logging
import utm
import pandas as pd

from . import dataset

class LocationApi:
    """utility for localizing tags in merged beep/node dataset"""
    def __init__(self, beep_filename, node_filename):
        """filenames of raw beep data and node location data"""
        self.beeps = dataset.BeepLocationDataset(beep_filename, node_filename) 
        # ez reference
        self.merged_df = self.beeps.df

        # assume utm zone, letter from first record
        self.zone = self.merged_df.iloc[0].zone
        self.letter = self.merged_df.iloc[0].letter

    def weighted_average(self, freq):
        """generate weighted average location dataset for given channel, tag_id and frequency"""
        mean_df = self.merged_df.resample(freq).mean()

        lats = []
        lngs = []
        for i, record in mean_df.iterrows():
            lat,lng = utm.to_latlon(record.node_x, record.node_y, self.zone, self.letter)
            lats.append(lat)
            lngs.append(lng)

        out_df = pd.DataFrame({
            'lat': lats,
            'lng': lngs,
        }, index=mean_df.index)

        # mean x,y from weighted node_x, node_y dataframe
        out_df['easting'] = mean_df.node_x
        out_df['northing'] = mean_df.node_y
        return out_df

