import pandas as pd

class DataFile:
    """generic csv data file abstraction"""
    def __init__(self, filename):
        """load filename into a pandas dataframe df"""
        self.filename = filename
        df = pd.read_csv(filename)
        self.df = self._clean_node_id(df)
        self.df = self._clean()

    def _clean(self):
        """logic for preparing the data frame for a given file type"""
        pass

    def _clean_node_id(self, df):
        """strip leading 0 from NodeId"""
        print('cleaning node id from file {}'.format(self.filename))
        if 'NodeId' in df.columns:
            print('found NodeId column')
            df.NodeId = df.NodeId.apply(lambda record: record.lstrip("0").upper())
        return df