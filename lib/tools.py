"""
Pandas tool lib for common functions/processes
"""

import re
import json
import threading
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
import difflib

import pandas as pd
import numpy as np
from spellchecker import SpellChecker

from . import logger, path
from .performance import timer


log = logger.getLogger(__name__)


def set_display_options(columns=None, rows=None):
    """
    Set some common options for display

    :param columns:
    :param rows:
    :return:
    """
    # Display options for pandas
    pd.set_option('display.max_columns', columns)
    pd.set_option('display.max_rows', rows)


@timer
def read_data(p, fn=pd.read_csv, encoding=None, strip_whitespaces=True,
              *args, **kwargs):
    """
    Read data and detect encoding of file if no encoding argument is passed.
    Strips whitespaces on load but can be set to False (we usually dont want
    whitespaces which is why I have it automatically do it for me).

    >>> df = read_data('dataset.csv')
    >>> df = read_data('dataset.csv', strip_whitespaces=False)

    :param p: Path to file
    :param fn: Function to read file
    :param encoding: Encoding of file
    :param strip_whitespaces: Clean whitespaces
    :return: DataFrame
    """

    # Get the encoding of the file if no encoding is found
    # Can take a while for large files
    encoding = encoding or path.detect_encoding(p)
    log.info(f'Encoding: {encoding}')

    # Run reach method
    df = fn(p, encoding=encoding, *args, **kwargs)

    # Strip whitespaces
    if strip_whitespaces:
        log.info(f'Stripping whitespaces from {Path(p).name}')
        df = str_strip(df)

    return df

def read_json(p):
    with open(p, 'r') as f:
        data = [json.loads(line) for line in f]
        return pd.json_normalize(data)

@timer
def export_data(p, df, df_export_fn=None, suffix='CLEAN', *args, **kwargs):
    """
    Export DataFrame to format of your choice using one of
    the DataFrame's to_* methods. Default is DataFrame.to_csv.

    >>> import pandas as pd
    >>>
    >>> df = pd.DataFrame([1, 2, 3], columns=['a', 'b', 'c'])
    >>> export_data(p, df)
    >>> export_data(p, df, df.to_json)
    >>> export_data(p, df, df.to_excel)

    :param p: Path to file
    :param df: DataFrame
    :param df_export_fn: Dataframe method to execute (i.e. `df.to_csv`)
    :param suffix: Suffix to add to filename
    :return:
    """
    export_path = path.get_cleaned_path(p, suffix=suffix)
    df_export_fn = df_export_fn or df.to_csv

    megabytes = memory_usage(df)
    log.info(f'Exporting {df.size} elements ({megabytes:.2f} MB) to {export_path}')
    df_export_fn(export_path, *args, **kwargs)
    return export_path

def memory_usage(df, size_format='MB'):
    """
    Calculate memory usage of DataFrame.

    :param df: DataFrame
    :param size_format: Size format of DataFrame whether in KB, MB, or GB
    :return: float
    """

    size_format = size_format.lower()
    if size_format == 'kb':
        size_format = 1
    elif size_format == 'mb':
        size_format = 2
    else:  # Gigabyte
        size_format = 3

    return df.memory_usage(index=True, deep=True).sum() / 1024 ** size_format

def str_strip(df_or_s, to_strip=None):
    """
    Strip whitespaces from a DataFrame and its column names or Series and from
    the Series name if name is stored in class.

    This is assuming we ALWAYS want to strip any leading and trailing
    whitespaces (because who really needs those).

    >>> str_strip(df_or_s)
    >>> str_strip(df_or_s, to_strip='##')

    :param df_or_s: DataFrame or Series
    :param to_strip: Strings to strip. If None, strips whitespace.
    :return: DataFrame or Series
    """

    # Copy object
    df_or_s_copy = df_or_s.copy()

    if isinstance(df_or_s_copy, pd.DataFrame):
        # Strip whitespaces from the columns
        df_or_s_copy.columns = df_or_s_copy.columns.str.strip()

        # Strip whitespaces from the Series if they are of type object
        for col in df_or_s_copy.select_dtypes(include=['object']).columns:
            try:
                df_or_s_copy[col] = df_or_s_copy[col].str.strip(to_strip)
            except AttributeError as e:
                log.error(f'Could not strip whitespaces for {col}:\n{e}')
    else:
        # Strip whitespaces from the Series
        df_or_s_copy = df_or_s_copy.str.strip(to_strip)

        # Strip whitespaces from the column name
        if df_or_s_copy.name:
            try:
                df_or_s_copy.name = df_or_s_copy.name.strip()
            except AttributeError as e:
                log.error(f'Could not strip whitespaces for {df_or_s_copy.name}:\n{e}')

    return df_or_s_copy

def values_counter(series):
    """
    Get a count of all unique values in a Series.
    (Just a wrapper for the `collections.Counter` class)

    >>> values_counter(pd.Series([1,2,3,4,5]))
    >>> values_counter(pd.Series([1,2,3,4,5,2,2,2]))

    :param series: Series
    :return: Counter
    """
    return Counter(series)

def has_duplicates(series):
    """
    Check if a Series has duplicate values.

    >>> has_duplicates(pd.Series([1,2,3,4,5]))
    >>> has_duplicates(pd.Series([1,2,3,4,5,2,2,2]))

    :param series: Series
    :return: bool
    """
    return series.duplicated().any()

def _values_counter_series_info(series, maximum=20):
    """
    Helper function to log information of value counts for a Series.

    :param series: Series
    :param maximum: Maximum number of values before having to inspect the
    Series manually.
    :return:
    """
    counter = values_counter(series)
    if len(counter) < maximum:
        log.info(f'{series.name}: <{series.dtype}> BEGIN')
        for value, count in counter.items():
            log.info(f'\t{value}: {count}')
        log.info(f'{series.name}: <{series.dtype}> END\n')
    else:
        # TODO: This is kind of ugly
        return series.name

def values_counter_info(df_or_s, max_values=20):
    """
    Get information of values for a DataFrame or Series.

    :param df_or_s: DataFrame or Series
    :param max_values: Maximum number of values before ignoring and having to
    inspect manually.
    """

    maximum_list = []
    if isinstance(df_or_s, pd.DataFrame):
        for column, series in df_or_s.items():
            exceeded = _values_counter_series_info(series, max_values)
            if exceeded:
                maximum_list.append(exceeded)
    else:
        exceeded = _values_counter_series_info(df_or_s, max_values)
        if exceeded:
            maximum_list.append(exceeded)

    if maximum_list:
        log.info(f'Columns {maximum_list} exceeded maximum values of {max_values}')

def error_counter(series, err_values=None):
    """
    Get a count of all error values in a Series. If `err_values` is `None`, it
    will use null values as the error values.

    :param series: Series
    :param err_values: list-of-error values. If `None`, it will use null values.
    :return: Total count of errors found.
    """

    if err_values is not None and not isinstance(err_values, (list, tuple, set)):
        err_values = [err_values]

    count = 0
    # Get the count of the found error values
    if err_values:
        counter = values_counter(series)
        for err_value in err_values:
            count += counter.get(err_value, 0)
    else:
        count = len(hasnull(series))
    return count

def error_rates(df_or_s, err_rate=None, err_values=None, as_pct=True):
    """
    Given a DataFrame or Series, check error rate of all elements. If
    `err_values` is `None`, it will check for null values as the error value.
    If argument `err_rate` is provided, only return elements that exceed rate.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA],
    >>>     'E':  [2,2,2]}
    >>> )
    >>>
    >>> error_rates(df)
    >>> error_rates(df, err_values='why')
    >>> error_rates(df, err_rate=.75, err_values=2)

    :param df_or_s: Dataframe
    :param err_rate: Acceptable error rate
    :type err_rate: float
    :param err_values: Error values to search for. If `None`, it will check
    for null values as the error value.
    :type err_values: list, tuple, set
    :param as_pct: If `True`, display error rate as percentage.
    :return: DataFrame of error rates and counts
    """

    columns = ['error_percent', f'error_count']
    err_table = pd.DataFrame(columns=columns)

    if isinstance(df_or_s, pd.DataFrame):
        for col, series in df_or_s.items():
            # Get the count of the found error values
            count = error_counter(series, err_values=err_values)

            # Error percent
            error_pct = count/series.size
            if err_rate is None or error_pct >= err_rate:
                if as_pct:
                    error_pct = f"{error_pct:.2%}"
                err_table.loc[col, columns[0]] = error_pct
                err_table.loc[col, columns[1]] = count
    else:
        # Get the count of the found error values
        count = error_counter(df_or_s, err_values=err_values)

        # Error percent
        error_pct = count / df_or_s.size
        if err_rate is None or error_pct >= err_rate:
            if as_pct:
                error_pct = f"{error_pct:.2%}"
            err_table.loc[0, columns[0]] = error_pct
            err_table.loc[0, columns[1]] = count
    return err_table

def error_rate(df_or_s, err_rate=None, err_values=None, as_pct=False):
    """
    Given a DataFrame or Series, get the error rate based on null values to
    total size of the provided DataFrame/Series.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> error_rate(df)
    >>> error_rate(df['B'])
    >>> error_rate(df['C'])

    :param df_or_s: DataFrame or Series
    :param err_rate: Acceptable error rate
    :param err_values: Error values to search for. If `None`, it will check
    :param as_pct: If `True`, display error rate as percentage.
    :return: float error rate
    """
    err_table = error_rates(df_or_s,
                            err_rate=err_rate,
                            err_values=err_values,
                            as_pct=False)

    # Get the length of what was returned to get total elements of returned
    # columns (rows from original DataFrame/Series * returned columns)
    elements_count = (df_or_s.shape[0] * len(err_table.index))
    err_pct = err_table['error_count'].sum()/ elements_count
    if as_pct:
        return f"{err_pct:.2%}"
    return err_pct

def isrisky(df_or_s, err_rate=.75, err_values=None):
    """
    Given a DataFrame or Series, check whether the Series is too error-prone
    to use based on the provided DataFrame and the `err_rate`.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> isrisky(df)
    >>> isrisky(df, err_rate=.75)
    >>> isrisky(df['C'])

    :param df_or_s: DataFrame or Series
    :param err_rate: Acceptable error rate
    :type err_rate: float
    :param err_values: Error values to search for
    :type err_values: any
    :return: bool
    """
    return error_rate(df_or_s, err_values=err_values) > err_rate

def risky_columns(df_or_s, err_rate=.75, err_values=None):
    return error_rates(df_or_s, err_rate=err_rate, err_values=err_values)

def get_filler_value(series, default=None, method='mean'):
    """
    Given a Series, get an appropriate filler value.
    # Todo: Make this a little more robust

    :param series: Series
    :param default: Default value to apply skipping the auto-generated filler
    value.
    :type default: Dictionary mapping of {type: value} or just a value.
    :param method:
    :return: filler value
    """

    # Check if default value is provided, use if so.
    if default is not None:
        if isinstance(default, dict):
            for typ, default_value in default.items():
                if typ == series.dtype:
                    return default[typ]
        else:
            return default

    # If type is an object or string
    if series.dtype in (object, str):
        return 'Not Available'

    # If an object is an int or float
    elif series.dtype in (int, float):
        if method == 'mean':
            return series.mean()
        elif method == 'median':
            return series.median()
        elif method == 'min':
            return series.min()-1
        elif method == 'max':
            return series.max()+1
        raise AttributeError(f'Method "{method}" is not supported for {series.dtype}')

    # If type is a datetime/Timestamp object
    elif pd.core.dtypes.common.is_datetime64_dtype(series):
        return pd.Timestamp.max

    # No filler value was found, raise AttributeError to fix
    raise AttributeError(f'No filler value for {series.dtype}')

def notnull(df_or_s):
    """
    Given either a DataFrame or a Series, return DataFrame/Series whose values
    are ALL not null.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> notnull(df)
    >>> notnull(df['C'])

    :param df_or_s: DataFrame or Series
    :return: DataFrame or Series of non-null values
    """
    if isinstance(df_or_s, pd.DataFrame):
        return df_or_s.loc[:, df_or_s.notnull().all(axis=0)]
    # df_or_s is a Series
    return df_or_s.loc[df_or_s.notnull()]

def hasnull(df_or_s):
    """
    Given either a DataFrame or a Series, return DataFrame/Series whose values
    have any null values.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> hasnull(df)
    >>> hasnull(df['C'])

    :param df_or_s: DataFrame or Series
    :return: DataFrame or Series of null values
    """

    if isinstance(df_or_s, pd.DataFrame):
        null_cols = []
        for col, series in df_or_s.loc[:, df_or_s.isnull().any(axis=0)].items():
            # Check if series has any null
            if series.isnull().any():
                null_cols.append(col)

        # Return only rows that have nulls in them (ignore valid rows)
        rows = df_or_s.loc[df_or_s.isnull().any(axis=1)].index.to_list()
        return df_or_s.loc[rows, null_cols]

    # df_or_s is a Series
    return df_or_s.loc[df_or_s.isnull()]

def allnull(df_or_s, axis=0):
    """
    Get columns/rows whose values are ALL null. These are essentially
    invalid rows/columns because we can't use them.

    For some reason.. axis in df.isnull().any(axis=*) is the opposite to
    everything else... 0 for columns and 1 for rows. Switching this function
    to keep with convention of 0 for rows and 1 for columns.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> allnull(df_or_s)
    >>> allnull(df_or_s.loc['C'])

    :param df_or_s: DataFrame or Series
    :param axis: 0 for rows, 1 for columns
    :return: DataFrame or Series of null values
    """

    if isinstance(df_or_s, pd.DataFrame):
        if axis == 0:
            # Get all null rows
            if df_or_s.isnull().all(axis=1).sum():
                return df_or_s.loc[df_or_s.isnull().all(axis=1), :]
        elif axis == 1:
            # Get all null columns
            if df_or_s.isnull().all(axis=0).sum():
                return df_or_s.loc[:, df_or_s.isnull().all(axis=0)]
        return pd.DataFrame()
    else:
        # Get all null rows of Series
        if df_or_s.isnull().all():
            return df_or_s.loc[df_or_s.isnull().all()]
        return pd.Series()

def fillnull(df_or_s, default=None, err_rate=None, *args, **kwargs):
    """
    Given a Dataframe or Series, fill it with null values.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> fillnull(df['C'])
    >>> fillnull(df, err_rate=.7)

    :param df_or_s: Dataframe or Series
    :param default: Dictionary of `{type: value}` or `value` default values to
    replace if you want to use your own default value(s) instead of the
    generated one.
    :param err_rate: Acceptable error rate
    :type err_rate: float
    :param args:
    :param kwargs:
    :return:
    """

    filler_values = {}
    # Copy or DataFrame or Series
    df_or_s_copy = df_or_s.copy()

    if isinstance(df_or_s_copy, pd.DataFrame):
        for col in df_or_s_copy.columns:
            if ((err_rate is None) or
                    (err_rate and not isrisky(df_or_s_copy[col], err_rate))):
                # Update filler_values dictionary
                filler_values[col] = get_filler_value(df_or_s_copy[col],
                                                      default=default)

                # Update the Series
                df_or_s_copy[col] = df_or_s_copy[col].fillna(
                    filler_values[col],
                    *args,
                    **kwargs
                )

    else:

        if ((err_rate is None) or
                (err_rate and not isrisky(df_or_s_copy, err_rate))):
            # Update the filler_values dictionary
            filler_values[df_or_s_copy.name] = get_filler_value(df_or_s_copy,
                                                                default=default)

            # Update the Series
            df_or_s_copy = df_or_s_copy.fillna(
                filler_values[df_or_s_copy.name],
                *args,
                **kwargs
            )

    return df_or_s_copy, filler_values

def null_info(df):
    """
    Get null info about the provided DataFrame.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,pd.NA,3],
    >>>     'B': [4,5,6],
    >>>     'C': [pd.NA,pd.NA,9],
    >>>     'D': [pd.NA,pd.NA,pd.NA]}
    >>> )
    >>>
    >>> null_info(df)

    :param df: DataFrame
    :return:
    """

    logger.separator('Null INFO', log_to_use=log)
    # Get columns that have no null values
    # not_null = notnull(df)

    # Get columns that contain null values
    has_null = hasnull(df)

    # Get all rows and columns whose values are ALL null
    all_null_rows = allnull(df, axis=0)
    all_null_columns = allnull(df, axis=1)

    log.info(f'{has_null.shape[1]}/{df.shape[1]} columns contain null values')
    log.info(f'{df.isnull().sum().sum()} total null values')
    log.info(f'{all_null_rows.shape[0]} row(s) contain ALL null values')
    if not all_null_rows.empty:
        for row in all_null_rows.index:
            log.info(f'\tRow "{row}"')
    log.info(f'{all_null_columns.shape[1]} column(s) contain ALL null values')
    if not all_null_columns.empty:
        for column in all_null_columns:
            log.info(f'\tColumn "{column}"')

    logger.separator('Risk Rate INFO', log_to_use=log)
    log.info(f'\n{error_rates(df)}')

    return has_null, all_null_rows, all_null_columns


def min_mean_median_max(series):
    """
    Just a helper function to get min, mean, median, and max values from
    a Series.

    :param series: Series
    :return:
    """
    return series.min(), series.mean(), series.median(), series.max()

def dtypes(df_or_s, flatten=False):
    """
    Get dtypes for a DataFrame or Series and return a DataFrame or Series
    of the same shape with data types for its values.

    :param df_or_s: DataFrame or Series
    :param flatten: Flatten to a Series of just the data types found
    :return: DataFrame or Series
    """

    df = df_or_s.copy()
    types = set()

    if isinstance(df_or_s, pd.DataFrame):

        for col, series in df_or_s.items():
            # The different types per index of series
            _types = []
            for index, value in series.items():
                # Get the value data type of series index
                typ = str(type(value)) if pd.notnull(value) else str(pd.NA)
                _types.append(typ)
                if flatten:
                    types.add(typ)

            # Assign them to the return DataFrame
            df[col] = _types
    else:
        for index, value in df_or_s.items():
            # Get the value data type of series index
            typ = str(type(value)) if pd.notnull(value) else str(pd.NA)
            df.loc[index] = typ
            if flatten:
                types.add(typ)

    return pd.Series(list(types)) if flatten else df

def dtypes_counter(df_or_s):
    """
    Get a count of data types for a DataFrame or Series. Returns a Dataframe
    or Series with the data types as its index and a count of each type for
    its values.

    :param df_or_s: DataFrame or Series
    :return: Dataframe or Series
    """

    types = dtypes(df_or_s, flatten=True)
    if isinstance(df_or_s, pd.DataFrame):
        # Create return DataFrame
        result = pd.DataFrame(index=types, columns=df_or_s.columns)

        # Iterate through the data types found
        for col, series in dtypes(df_or_s).items():
            # Get duplicates count
            counter = values_counter(series)
            for value, count in counter.items():
                result.loc[value, col] = count
    else:
        # Create turn Series
        result = pd.Series(index=types, name=df_or_s.name)

        # Get duplicates count
        counter = values_counter(dtypes(df_or_s))
        for value, count in counter.items():
            result.loc[value] = count

    result = result.fillna(0)
    result = result.astype(int)
    return result

def has_different_dtypes(df_or_s):
    """
    Check if DataFrame or Series has different dtypes.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': [1,'two',3],
    >>>     'B': [4,5,6],
    >>>     'C': [7.0,8,9],
    >>>     'D': [10,11,12]}
    >>> )
    >>>
    >>> diff_types = has_different_dtypes(df)
    >>> diff_types['has_different_types'].sum()
    >>> diff_types.attrs['has_different_types']

    :param df_or_s: DataFrame or Series
    :return: DataFrame of bools whether a DataFrame or Series has different
    dtypes (and if they have any null values).
    """

    if isinstance(df_or_s, pd.Series):
        df_or_s = pd.DataFrame(df_or_s)

    # Columns for the result DataFrame
    columns = ['has_different_types', f'has_{pd.NA}']

    # Get the different data types for the DataFrame or Series
    types = dtypes(df_or_s)

    # Create the result DataFrame
    result = pd.DataFrame(columns=columns,
                          index=df_or_s.columns)

    for col, series in types.items():
        # The found data types
        found_types = series.unique()

        # Check if `NaN` is in the found data types
        if str(pd.NA) in found_types:
            # If so remove from our list of found types because we don't want
            # to count that as a different data type.
            result.loc[col, columns[1]] = len(hasnull(df_or_s.loc[:, col]))
            found_types = np.delete(found_types, np.where(found_types == str(pd.NA)))
        else:
            result.loc[col, columns[1]] = 0

        # Check if our found_types is larger than 1 (if it is larger than 1
        # we have multiple data types for this Series)
        result.loc[col, columns[0]] = len(found_types) > 1

    # Adding metadata for ease-of-use. df.attrs['has_different_types']
    # Can just as easily query the data from the DataFrame
    result.attrs[columns[0]] = result[columns[0]].sum()
    return result

def get_values_of_dtypes(series, types):
    """
    Get values of a certain type for a Series. Useful if there are multiple
    data types in a Series.

    :param series: Series
    :param types: type to filter by. Can either by a single type or a list of
    types.
    :return: Filtered Series of found data types
    """
    return series[series.apply(lambda x: isinstance(x, types))]


def typos(txt, split=None):
    """
    Check if a string contains typos.

    :param txt: Text to check
    :param split: Split string by character
    :return: set of found typos
    """
    return SpellChecker().unknown(txt.split(split))


def typos_corrections(misspelled):
    """
    Suggest the best possible typo corrections based on a set of misspelled
    words.

    :param misspelled: Set of misspelled words
    :return: Dictionary of typo corrections
    """
    spell = SpellChecker()
    corrections = {}
    for word in misspelled:
        corrections[word] = spell.correction(word)
    return corrections

def _get_closest_matches_series(series, n=2, cutoff=.8):
    """
    Helper function to get the closest matches of items in a Series.

    :param series:
    :param n:
    :param cutoff:
    :return:
    """
    result = set()
    if series.dtype == 'object':
        for idx, item in series.items():
            closest_matches = difflib.get_close_matches(item, series.values, n=n, cutoff=cutoff)
            if len(set(closest_matches)) > 1:
                for closest_match in closest_matches:
                    result.add(closest_match)

    return result

def messy_strings(df_or_s, n=2, cutoff=.8):
    """
    Given a DataFrame or Series, return a set of values that are similarly
    named to handle messy duplicate/misspelled words. Will only work on
    the 'object'/str data type.

    >>> import pandas as pd
    >>> df = pd.DataFrame(
    >>>     {'A': ['john', 'jon', 'johnny'],
    >>>     'B': ['bob', 'bobby', 'hob'],
    >>>     'C': ['kyle', 'phil', 'dean'],
    >>>     'D': ['tim', 'jim', 'den']}
    >>> )
    >>> messy_strings(df)

    :param df_or_s: DataFrame or Series
    :param n: The maximum number of close matches to return. The
    default value is 3.
    :param cutoff: A float between 0.0 and 1.0. Possibilities with a
    similarity ratio below this cutoff are ignored. The default value is 0.6.
    A higher cutoff requires a closer match.
    :return:
    """

    result = set()
    if isinstance(df_or_s, pd.DataFrame):
        for col, series in df_or_s.items():
            closest = _get_closest_matches_series(series, n=n, cutoff=cutoff)
            if closest:
                result.update(closest)
    else:
        closest = _get_closest_matches_series(df_or_s, n=n, cutoff=cutoff)
        if closest:
            result.update(closest)
    return result

@timer
def info(df):
    """
    Get a comprehensive set of information for the provided DataFrame.

    :param df: DataFrame
    """

    null_info(df)

    logger.separator('Data Types INFO', log_to_use=log)
    log.info(f'\n{has_different_dtypes(df)}')
    logger.separator(log_to_use=log)
    log.info(f'\n{dtypes_counter(df)}')

    logger.separator('Values Counter INFO', log_to_use=log)
    values_counter_info(df)

    df.info()


def parse_list(s, sep=','):

    result = {}
    for idx, item in s.items():
        split = item.split(sep)
        result[idx] = split if any(split) else []

    return result

def convert_camel_case(name, replace=' '):
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub(replace, name).lower()

def get_dict_by_messy_string(d, find=None, case_sensitive=False):
    if find is None:
        return d
    elif isinstance(find, str) or not isinstance(find, Iterable):
        find = [find]

    normalize = (lambda x: x) if case_sensitive else str.lower
    needles = [normalize(f) for f in find]

    return {
        k: v
        for k, v in d.items()
        if any(n in normalize(k) for n in needles)
    }

