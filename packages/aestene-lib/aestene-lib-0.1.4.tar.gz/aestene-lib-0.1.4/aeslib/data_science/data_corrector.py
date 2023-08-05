# This functionality is courtesy of Anton Eskov (@antoneskov)
import datetime as dt
from abc import ABC, abstractmethod

import pandas as pd

from aeslib.data_science.utility import Utility
from aeslib.data_engineering.azure_tools import AzureKeyvaultHelper
from aeslib.data_science.interval_analysis import IntervalAnalysis, IntervalAnalysisMulti


class DataCorrectorBase(ABC):

    @abstractmethod
    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        pass

    def get_freq(self, df: pd.DataFrame)->dt.timedelta:
        return Utility.get_freq(df)


class StateRunDataCorrector(DataCorrectorBase):
    def __init__(self,
                 keyvault: AzureKeyvaultHelper,
                 df_tags: pd.DataFrame,
                 statecol_pattern: str = 'StateRun (End)',
                 interpolate: bool = True):
        self.keyvault = keyvault
        self.df_tags = df_tags
        self.statecol_pattern = statecol_pattern
        self.interpolate = interpolate

    # Assuming Time indexed dataframe
    def correct_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        assert df is not None
        assert len(df) > 2

        df_state_end = df.columns[df.columns.str.contains(self.statecol_pattern)]
        if self.interpolate:
            df_state_end.fillna(method='pad', inplace=True)
        df.update(df_state_end)

        return df

class MultiIndexDataCorrector(DataCorrectorBase):
    def __init__(self, level0: str, level1: str):
        self.level0 = level0
        self.level1 = level1

    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        res = df.drop(columns=['Unnamed: 0'])
        res.reset_index(inplace=True)
        res.set_index([self.level0, self.level1], inplace=True)
        return res


class TimeZoneDataCorrector(DataCorrectorBase):
    def __init__(self,
                 tz_source='Europe/London',
                 tz_dest='UTC',
                 ambiguous='infer',
                 neutralize_tz: bool = True,
                 level_name='TimeStamp'):
        self.tz_source = tz_source
        self.ambiguous = ambiguous
        self.tz_dest = tz_dest
        self.neutralize_tz = neutralize_tz
        self.level_name = level_name

    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        level = self.level_name if isinstance(df.index, pd.MultiIndex) else None
        res = df.tz_localize(self.tz_source,
                             ambiguous=self.ambiguous,
                             copy=False,
                             level=level).tz_convert(self.tz_dest, level=level)
        if self.neutralize_tz:
            res = res.tz_convert(None, level=level)
        res.sort_index(inplace=True)
        return res
    
# Assumption:
#  data Index - DateTime, timezone neutral, contains UTC timestamps (no duplicates)
#  cols_to_interpolate does not include "step columns"
class InterpolateDropDataCorrector(DataCorrectorBase):
    def __init__(self, drop_threshold: dt.timedelta, cols_to_interpolate=None, method='linear'):
        self.drop_threshold = drop_threshold
        self.cols_to_interpolate = cols_to_interpolate
        self.method = method
        self.all_intervals = None
        self.dropped_intervals = None


    def get_empty_intervals(self, df: pd.DataFrame)-> pd.DataFrame:
        cols = df.columns if self.cols_to_interpolate is None else self.cols_to_interpolate
        return IntervalAnalysis.get_empty_intervals(df, cols)


    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        cols_to_interpolate = \
            df.columns if self.cols_to_interpolate is None else self.cols_to_interpolate

        # Prepare list of intervals
        df_interval = self.get_empty_intervals(df)

        # Drop big intervals
        df_drops = df_interval[df_interval.duration > self.drop_threshold]
        dfres = df

        for drop in df_drops.itertuples():
            dfres = dfres.drop(axis=0, index=dfres.loc[(dfres.index > drop.interval.left) \
                & (dfres.index < drop.interval.right)].index)

        # Interpolate
        dfres[cols_to_interpolate] = dfres[cols_to_interpolate].interpolate(method=self.method,
                                                                            axis=0)

        self.all_intervals = df_interval
        self.dropped_intervals = df_drops
        return dfres

# Assumption:
#  data Index - DateTime, timezone neutral, contains UTC timestamps (no duplicates)
#  cols_to_interpolate does not include "step columns"
class InterpolateDropMultiDataCorrector(InterpolateDropDataCorrector):
    # def __init__(self, drop_threshold: dt.timedelta, cols_to_interpolate = None, method='linear'):
    #     self.drop_threshold = drop_threshold
    #     self.cols_to_interpolate = cols_to_interpolate
    #     self.method = method
    #     self.all_intervals = None
    #     self.dropped_intervals = None


    def get_empty_intervals(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = df.columns if self.cols_to_interpolate is None else self.cols_to_interpolate
        return IntervalAnalysisMulti.get_empty_intervals(df, cols)


    def correct_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        slice_levels = IntervalAnalysisMulti.get_slice_levels(df)
        timeindex_name = IntervalAnalysisMulti.get_timeindex_name(df)
        dfres = None
        for slicer, df_slice in IntervalAnalysisMulti.iterate_time_levels(df):
            df_corrected = super().correct_dataframe(df_slice)
            df_corrected.reset_index(inplace=True)

            if len(slice_levels) == 1:
                slicer = [slicer]
        
            for idx, level in enumerate(slice_levels):
                df_corrected[level] = slicer[idx]

            dfres = df_corrected if dfres is None else pd.concat([dfres, df_corrected], axis=0)


        dfres.set_index(slice_levels + [timeindex_name], inplace=True)
        dfres.sort_index(level=dfres.index.names, inplace=True)
        return dfres


class DataCorrector:
    @staticmethod
    def execute(df: pd.DataFrame, df_tagids: pd.DataFrame, interpolate: bool = True) ->pd.DataFrame:
        keyvault = AzureKeyvaultHelper(key_vault_name='arnts-keyvault')
        sr_corrector = StateRunDataCorrector(keyvault=keyvault,
                                             df_tags=df_tagids,
                                             interpolate=interpolate)
        # Add more correctors and execute these in a sequence, if needed
        return sr_corrector.correct_dataframe(df)
        