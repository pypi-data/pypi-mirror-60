import datetime as dt

import numpy as np
import pandas as pd
from scipy import stats

def add_rolling_features(df: pd.DataFrame,
                         columns: list,
                         window: dt.timedelta,
                         rolling_sum: bool = True,
                         rolling_mean: bool = True,
                         rolling_std: bool = True):
    dfs = [df]
    df_rolling = df[columns]
    
    if rolling_sum:
        df_sum = df_rolling.rolling(window=window).sum()
        df_sum.columns = [c + "_rolling_sum" for c in df_sum.columns]
        dfs.append(df_sum)
    
    if rolling_mean:
        df_mean = df_rolling.rolling(window=window).mean()
        df_mean.columns = [c + "_rolling_mean" for c in df_mean.columns]
        dfs.append(df_mean)
    
    if rolling_std:
        df_std = df_rolling.rolling(window=window).std()
        df_std.columns = [c + "_rolling_std" for c in df_std.columns]
        dfs.append(df_std)
    
    df = pd.concat(dfs, axis=1)
    return df

def set_negative_values_to_zero(df: pd.DataFrame, columns: list):
    df_columns = df[columns]
    df_columns[df_columns < 0] = 0
    df.update(df_columns)
    return df

def add_day_integer_column(df: pd.DataFrame):
    day_column = pd.Series(data=[timestamp.day for timestamp in df.index.to_series()],
                           index=df.index)
    df['day'] = day_column
    return df

def add_month_integer_column(df: pd.DataFrame):
    month_column = pd.Series(data=[timestamp.month for timestamp in df.index.to_series()],
                             index=df.index)
    df['month'] = month_column
    return df

def drop_outliers(df: pd.DataFrame, stddev_threshold: int = 3):
    return df[np.abs(stats.zscore(df) < stddev_threshold).all(axis=1)]
