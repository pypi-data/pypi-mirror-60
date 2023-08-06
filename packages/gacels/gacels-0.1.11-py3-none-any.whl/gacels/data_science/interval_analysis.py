# This functionality is courtesy of Anton Eskov (@antoneskov)

from typing import List
import datetime as dt
import random

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from gacels.data_science.utility import Utility

class IntervalAnalysis:
    def __init__(self, df_interval: pd.DataFrame):
        self.df_interval = df_interval

    # Merge overlapping intervals
    # intervals: List containing intervals sorted by start time
    # closed: 'closed' interval value for evt. new intervals
    @staticmethod
    def merge_overlapping_intervals(intervals: List, closed: str = 'neither')->List:
        assert len(intervals) > 0, 'Not enough data in "intervals"'
        merged = [intervals[0]]
        for interval in intervals:
            top = merged[-1]
            if top.overlaps(interval) and (interval.right > top.right):
                top = pd.Interval(left=top.left, right=interval.right, closed=closed)
            elif not top.overlaps(interval):
                merged.append(interval)
        return merged

    @classmethod
    def get_empty_intervals(cls, df: pd.DataFrame, cols: List = None)-> pd.DataFrame:
        freq = Utility.get_freq(df)

        res = pd.Series()
        cols = df.columns.to_list() if cols is None else cols

        for icol, colname in enumerate(cols):
            idx = df[colname].dropna().index
            
            # Compensate for leading nan
            if pd.isna(df.iloc[0, icol]):
                idx = idx.insert(0, df.index[0]-freq)
                
            ser1 = pd.Series(idx.tolist(), index=idx)
            ser2 = ser1.shift(-1)-ser1
            ser2 = ser2[ser2 != freq]
            res = res.append(ser2)
            
        res = res.dropna()

        # Group res by start time. Max length to be used to generate intervals.
        resgrp = res.groupby(level=0).agg(ucnt='nunique', valmax='max', valmin='min', cnt='count')
        # Generate intervals by (start_time, start_time + max(length))
        ser_interval = \
            resgrp.apply(lambda x: pd.Interval(x.name,
                                               x.name+x['valmax'],
                                               closed='neither'),
                         axis=1)
        if not ser_interval.empty:

            merged = IntervalAnalysis.merge_overlapping_intervals(ser_interval.sort_values())

            # Create data frame with merged intervals.
            df_interval = pd.DataFrame(data={'interval': merged}, index=[x.left for x in merged])
            df_interval['duration'] = \
                df_interval.apply(lambda x: x['interval'].right - x['interval'].left, axis=1)
            df_interval['duration_min'] = \
                df_interval.apply(lambda x: x['duration'].total_seconds()/60, axis=1)

            return df_interval
        else:
            return ser_interval
    
    @staticmethod
    def plot_distribution(df_interval: pd.DataFrame,
                          cut_durations: dt.timedelta = None,
                          figsize: tuple = (16, 16),
                          bins=50):
        df = df_interval if cut_durations is None \
             else df_interval[df_interval.duration < cut_durations]
        plt.figure(figsize=figsize)
        df.duration_min.plot.hist(bins=bins)
        plt.gca().set(title="Distribution of missing data duration (min)",
                      xlabel="Duration, min",
                      ylabel="Frequency")
        plt.show()
    
    @staticmethod
    def get_timeline(df_interval: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        df_timeline = pd.DataFrame(
            data={'dur':0},
            index=pd.DatetimeIndex(pd.date_range(
                start=df.index[0],
                end=df.index[-1],
                freq=Utility.get_freq(df)))).merge(
                    right=df_interval,
                    how='outer',
                    left_index=True,
                    right_index=True)
        df_timeline.loc[~pd.isna(df_timeline.duration_min), 'dur'] = \
            df_timeline.loc[~pd.isna(df_timeline.duration_min), 'duration_min']
        df_timeline.index = df_timeline.index.tz_localize(None)
        return df_timeline

    @staticmethod
    def plot_timeline(df_interval: pd.DataFrame, df: pd.DataFrame, figsize: tuple = (16, 16)):
        plt.figure(figsize=figsize)
        df_timeline = IntervalAnalysis.get_timeline(df_interval, df)
        df_timeline.dur.plot()
        plt.gca().set(title="Missing data duration (min) timeline",
                      xlabel="Time",
                      ylabel="Duration, min")
        plt.show()

        # df - original data set
        # df_interval: data frame containing 'empty' intervals, as returned by get_empty_intervals
        # method - Pandas interpolation method, e.g.:
                # method = 'linear'
                # method = 'pad'
                # method = 'time'
                # method = 'quadratic'
                # method = 'cubic'
        # missing_lengths - number of missing data points for each missing interval. E.g.:
                # missing_lengths = [x if x!=0  else 1 for x in range(0,21, 5) ]
        # nmissing = 15 #Number of missing intervals in each 'good' interval
        # min_neighbours = 1 #Guaranteed number of neighbours around missing


    @staticmethod
    def threshold_experiment(df: pd.DataFrame,
                             df_interval: pd.DataFrame,
                             method: str,
                             missing_lengths: List,
                             cols: List = None,
                             big_enough: dt.timedelta = dt.timedelta(days=10),
                             nmissing: int = 15,
                             min_neighbours: int = 1) -> pd.DataFrame:
        # find "Good" intervals
        df_good_interval = pd.DataFrame(
            data={'left': df_interval.interval.apply(lambda x: x.right),
                  'right':df_interval.shift(-1).interval.apply(lambda x: x.left
                                                               if not pd.isna(x)
                                                               else df.iloc[-1].name)})
        df_good_interval['duration'] = df_good_interval.right-df_good_interval.left
        # Iterate through 'good intervals' which are big enough
        # build a test dataframe with orig and interpolated columns
        # drop random data points

        periods = range(len(df_good_interval.loc[df_good_interval.duration >= big_enough]))
        cols_analyzed = df.columns.to_list() if cols is None else cols
        df_errs = pd.DataFrame(columns=cols_analyzed,
                               index=pd.MultiIndex.from_product([missing_lengths, periods],
                                                                names=['gap_length', 'period']))

        # Loop through columns
        for colname in cols_analyzed:

            for missing_length in missing_lengths:
                period = 0
                for row in df_good_interval.loc[df_good_interval.duration >= big_enough].itertuples():
                    df_test = pd.DataFrame(
                        data={'x': np.arange(len(df.loc[row.left:row.right, colname])),
                              'orig':df.loc[row.left:row.right, colname],
                              'interpolated': df.loc[row.left:row.right, colname]},
                        index=df.loc[row.left:row.right].index)
                    ndrops = \
                        sorted([random.randint(min_neighbours, \
                            len(df_test)-1-min_neighbours-missing_length)\
                            for x in range(nmissing)])
                    
                    # Check for and remove overlapping missing intervals
                    ndrops_corr = [ndrops[0]]
                    for ndrop in ndrops:
                        acur = ndrops_corr[-1]
                        if acur+missing_length > ndrop:
                            continue
                        else:
                            ndrops_corr.append(ndrop)
                            
                    ndrops = sorted([x+j for j in range(missing_length) for x in ndrops_corr])
                    df_test.iloc[ndrops, df_test.columns.get_loc('interpolated')] = np.nan
                    df_fixed = df_test['interpolated'].interpolate(method=method, axis=0)
                    df_errs.loc[(missing_length, period), colname] = \
                        Utility.mean_absolute_percentage_error(df_test.orig, df_fixed)
                    period += 1
        df_errs = df_errs.astype('float')
        return df_errs

    @staticmethod
    def plot_threshold_experiment(df_errs: pd.DataFrame, method: str, figsize: tuple = (16, 16)):
        df_errs_mean = df_errs.groupby('gap_length').mean()
        #df_errs_sem = df_errs.groupby('gap_length').sem()
        plt.figure()
        df_errs_mean.plot(figsize=figsize)
        plt.xlabel("Missing gap size, data points")
        plt.ylabel("MAPE, %")
        plt.suptitle(f"{method} Interpolation error (MAPE) by missing gap size")
        plt.show()

class IntervalAnalysisMulti(IntervalAnalysis):

    #
    #   Returns a list of MultiIndex levels preceeding DatetimeIndex level
    #
    @staticmethod
    def get_slice_levels(df: pd.DataFrame) -> List:
        assert isinstance(df.index, pd.MultiIndex),\
             "Use IntervalAnalysis class for single-indexed data frames"
        slice_levels = []

        for level in df.index.levels:
            if  isinstance(level, pd.DatetimeIndex):
                break
            slice_levels.append(level.name)
        return slice_levels

    @staticmethod
    def get_timeindex_name(df: pd.DataFrame) -> str:
        assert isinstance(df.index, pd.MultiIndex),\
            "Use IntervalAnalysis class for single-indexed data frames"

        for level in df.index.levels:
            if isinstance(level, pd.DatetimeIndex):
                return level.name
        return None


    @staticmethod
    def iterate_time_levels(df: pd.DataFrame):

        slice_levels = IntervalAnalysisMulti.get_slice_levels(df)

        for slicer in df.index.to_frame().reset_index(drop=True).groupby(slice_levels).size().index:
            yield slicer, df.loc[slicer]


    @classmethod
    def get_empty_intervals(cls, df: pd.DataFrame, cols: List = None)-> pd.DataFrame:
        
        slice_levels = IntervalAnalysisMulti.get_slice_levels(df)
        timeindex_name = IntervalAnalysisMulti.get_timeindex_name(df)
        dfres = None

        for slicer, dfslice in IntervalAnalysisMulti.iterate_time_levels(df):
            df_interval = super(IntervalAnalysisMulti, cls).get_empty_intervals(dfslice, cols)
            df_interval.reset_index(inplace=True)
            df_interval.rename(columns={'index':timeindex_name}, inplace=True)
            if len(slice_levels) == 1:
                slicer = [slicer]
        
            for idx, level in enumerate(slice_levels):
                df_interval[level] = slicer[idx]

            dfres = df_interval if dfres is None else pd.concat([dfres, df_interval], axis=0)
        dfres.set_index(slice_levels + [timeindex_name], inplace=True)
        return dfres

    @staticmethod
    def get_timeline(df_interval: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    @staticmethod
    def plot_distribution(df_interval: pd.DataFrame,
                          cut_durations: dt.timedelta = None,
                          figsize: tuple = (16, 16),
                          bins=50):
        raise NotImplementedError

    @staticmethod
    def plot_threshold_experiment(df_errs: pd.DataFrame, method: str, figsize: tuple = (16, 16)):
        raise NotImplementedError

    @staticmethod
    def plot_timeline(df_interval: pd.DataFrame, df: pd.DataFrame, figsize: tuple = (16, 16)):
        raise NotImplementedError

    @staticmethod
    def threshold_experiment(df: pd.DataFrame,
                             df_interval: pd.DataFrame,
                             method: str,
                             missing_lengths: List,
                             cols: List = None,
                             big_enough: dt.timedelta = dt.timedelta(days=10),
                             nmissing: int = 15,
                             min_neighbours: int = 1) -> pd.DataFrame:
        raise NotImplementedError
        