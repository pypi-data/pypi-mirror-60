import logging
import pandas as pd
from station.data.rawbeepfile import RawBeepFile
from station.data.nodelocationfile import NodeLocationFile

class BeepLocationDataset:
    """dataframe for merged beep / node location"""
    def __init__(self, beep_filename, node_filename):
        """filenames of raw beep data and node location data"""
        logging.info('loading datasets from beep file:{};  node location file:{}'.format(beep_filename, node_filename))
        self.beeps = RawBeepFile(filename=beep_filename)
        self.nodes = NodeLocationFile(filename=node_filename)
        # merged location dataframe
        self.df = None
        self._merge()

    def _merge(self):
        """merge beep dataset with node location dataset"""
        df = self.beeps.df.merge(right=self.nodes.df, left_on='NodeId', right_on='NodeId')
        delta = self.beeps.beep_count() - df.shape[0]
        if delta > 0:
            logging.info('dropped {:,} records after merging node locations'.format(delta))
        self.df = df