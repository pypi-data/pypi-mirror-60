"""Tools to manipulate Pandas DataFrames for Data Science tasks.
"""
import pandas as pd

def set_rows_to_display_pandas(rows: int):
    """Set the number of rows Pandas will display when showing a DataFrame.

    Arguments:
        rows {int} -- Number of rows.
    """
    pd.options.display.max_rows = rows

def print_data_frame(df: pd.DataFrame, max_rows=5, max_columns=7, width=None):
    with pd.option_context(
            'display.max_rows', max_rows,
            'display.max_columns', max_columns,
            'display.width', width):
        print(df)

def get_idxmax_integer_pos_of_series(series: pd.Series) -> int:
    """Get the index of the largest entry in a Pandas series as an integer.

    Arguments:
        series {pd.Series} -- Series

    Returns:
        int -- Integer index of maximum value
    """
    current_index = 0
    max_index = 0
    max_value = 0
    for value in series:
        if value > max_value:
            max_value = value
            max_index = current_index
        current_index += 1
    return max_index

def read_csv_files(csv_files: list) -> list:
    csv_data_frames = []
    for filename in csv_files:
        df = pd.read_csv(filename, sep=';')
        csv_data_frames.append(df)
    return csv_data_frames

def stack_csv_files(csv_files: list, write_to_file=False) -> pd.DataFrame:
    csv_data_frames = read_csv_files(csv_files)
    stacked_data_frame = pd.concat(csv_data_frames, axis=0, ignore_index=True)
    stacked_data_frame.drop(stacked_data_frame.columns[0], axis=1, inplace=True)
    if write_to_file:
        stacked_data_frame.to_csv('stacked-dataframe.csv', sep=';', index=False)

    return stacked_data_frame

def check_for_columns_with_no_data_or_variation(df: pd.DataFrame):
    description = df.describe().T
    print("N Total columns         : {}".format(len(description)))
    print("N Cols with no data     : {}".format(len(description.loc[description['count'] == 0])))
    print("N Cols with no variation: {}".format(len(description.loc[description['std'] == 0])))

def count_all_columns(df: pd.DataFrame) -> pd.Series:
    return df.count()

def get_interval_size_with_consecutive_null(df: pd.DataFrame, column):
    intervals = \
        df[column].isnull().astype(int).groupby(df[column].notnull().astype(int).cumsum()).sum()
    return intervals

def remove_rows_with_zero_value(series: pd.Series):
    return series[series != 0]

def count_null_values_in_columns(df: pd.DataFrame):
    return df.isnull().sum()

def percentage_of_values_that_is_null(df: pd.DataFrame):
    return (count_null_values_in_columns(df) / len(df))*100

def show_columns_with_zero_variation(df: pd.DataFrame):
    description = df.describe()
    return description.loc[:, description.loc['std'] == 0]
