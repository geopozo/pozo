import pytest
import numpy as np
import pandas as pd
import polars as pl
from pozo.utils import summarize_array, is_close, hash_array, min_data, max_data, isfinite_data

list_data = [float('inf'), -float('inf'), None]
list_data_irregular = [0, 20, 40, 50, 70, 90, 300, 301, 330, 400]
np_data = np.linspace(0, 2000, num=50, endpoint=True)
np_data_irregular = np.array(list_data_irregular)
df = pd.Series(np_data)
df_data_irregular = pd.Series(np_data_irregular)
df_polars = pl.Series(np_data)
df_polars_data_irregular = pl.Series(np_data_irregular)

def test_summarize_array():
    assert summarize_array(np_data) is not None
    assert summarize_array(df) is not None
    assert summarize_array(df_polars) is not None
    assert summarize_array(list_data) is None
    assert summarize_array(np_data_irregular) is not None
    assert summarize_array(df_data_irregular) is not None
    assert summarize_array(df_polars_data_irregular) is not None
    assert summarize_array(list_data_irregular) is None

def test_is_close():
    assert is_close(np_data[0], np_data[-1], True, np_data[1]-np_data[0], 0.001) is not None
    assert is_close(df[0], df[-1], True, df[1]-df[0], 0.001) is not None
    assert is_close(df_polars[0], df_polars[-1], True, df_polars[1]-df_polars[0], 0.001) is not None
    assert is_close(list_data[0], list_data[-1], True, list_data[1]-list_data[0], 0.001) is not None
    assert is_close(np_data_irregular[0], np_data_irregular[-1], True, np_data_irregular[1]-np_data_irregular[0], 0.001) is not None
    assert is_close(df_data_irregular[0], df_data_irregular[-1], True, df_data_irregular[1]-df_data_irregular[0], 0.001) is not None
    assert is_close(df_polars_data_irregular[0], df_polars_data_irregular[-1], True, df_polars_data_irregular[1]-df_polars_data_irregular[0], 0.001) is not None
    assert is_close(list_data_irregular[0], list_data_irregular[-1], True, list_data_irregular[1]-list_data_irregular[0], 0.001) is not None

def test_hash_array():
    assert hash_array(np_data) is not None
    assert hash_array(df) is not None
    assert hash_array(df_polars) is not None
    assert hash_array(list_data) is not None
    assert hash_array(np_data_irregular) is not None
    assert hash_array(df_data_irregular) is not None
    assert hash_array(df_polars_data_irregular) is not None
    assert hash_array(list_data_irregular) is not None


def test_min_data():
    assert min_data(np_data) is None
    assert min_data(df) is None
    assert min_data(df_polars) is None
    assert min_data(list_data) is None
    assert min_data(np_data_irregular) is None
    assert min_data(df_data_irregular) is None
    assert min_data(df_polars_data_irregular) is None
    assert min_data(list_data_irregular) is None


def test_max_data():
    assert max_data(np_data) is None
    assert max_data(df) is None
    assert max_data(df_polars) is None
    assert max_data(list_data) is None
    assert max_data(np_data_irregular) is None
    assert max_data(df_data_irregular) is None
    assert max_data(df_polars_data_irregular) is None
    assert max_data(list_data_irregular) is None


def test_isfinite_data():
    assert isfinite_data(np_data[0]) is None
    assert isfinite_data(df[0]) is None
    assert isfinite_data(df_polars[0]) is None
    assert isfinite_data(list_data[0]) is None
    assert isfinite_data(np_data_irregular[0]) is None
    assert isfinite_data(df_data_irregular[0]) is None
    assert isfinite_data(df_polars_data_irregular[0]) is None
    assert isfinite_data(list_data_irregular[0]) is None

