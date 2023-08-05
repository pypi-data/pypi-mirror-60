import datetime as dt
import pandas as pd
import numpy as np

class Utility:

    @staticmethod
    def get_freq(df: pd.DataFrame) -> dt.timedelta:
        assert len(df) > 2, "Not enough data in the data set"

        check_level = None

        #Compensate for MultiIndex - find Datetime level
        if isinstance(df.index, pd.MultiIndex):
            for level in df.index.levels:
                if isinstance(level, pd.DatetimeIndex):
                    check_level = level
                    break
        elif isinstance(df.index, pd.DatetimeIndex):
            check_level = df.index

        assert check_level is not None, "Cannot define frequency - no DatetimeIndex given"
        return check_level[1]-check_level[0]

    @staticmethod
    def mean_absolute_percentage_error(y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
