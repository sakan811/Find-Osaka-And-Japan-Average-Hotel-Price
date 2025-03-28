import numpy as np
import pandas as pd

from japan_avg_hotel_price_finder.graphql_scraper_func.graphql_data_extractor import extract_hotel_data


def test_extract_hotel_data_multiple_appends():
    # Sample hotel data
    hotel_data_list_1 = [
        {
            "displayName": {"text": "Hotel A"},
            "basicPropertyData": {"reviewScore": {"score": 4.5}},
            "blocks": [{"finalPrice": {"amount": 150}}],
            "location": {'displayLocation': 'Osaka'}
        }
    ]
    hotel_data_list_2 = [
        {
            "displayName": {"text": "Hotel B"},
            "basicPropertyData": {"reviewScore": {"score": 4.0}},
            "blocks": [{"finalPrice": {"amount": 200}}],
            "location": {'displayLocation': 'Tokyo'}
        }
    ]

    df_list = []

    # Call the function twice with different data
    extract_hotel_data(df_list, hotel_data_list_1)
    extract_hotel_data(df_list, hotel_data_list_2)

    # Assertions
    assert len(df_list) == 2
    df1 = df_list[0]
    df2 = df_list[1]

    assert df1.shape == (1, 4)
    assert df1['Hotel'].tolist() == ['Hotel A']
    assert df1['Review'].tolist() == [4.5]
    assert df1['Price'].tolist() == [150]
    assert df1['Location'].tolist() == ['Osaka']

    assert df2.shape == (1, 4)
    assert df2['Hotel'].tolist() == ['Hotel B']
    assert df2['Review'].tolist() == [4.0]
    assert df2['Price'].tolist() == [200]
    assert df2['Location'].tolist() == ['Tokyo']


def test_extract_hotel_data_missing_values():
    # Sample hotel data with missing values
    hotel_data_list = [
        {
            "displayName": None,
            "basicPropertyData": {"reviewScore": {"score": 4.5}},
            "blocks": [{"finalPrice": {"amount": 150}}],
            "location": {'displayLocation': 'Osaka'}
        },
        {
            "displayName": {"text": "Hotel B"},
            "basicPropertyData": None,
            "blocks": None,
            "location": None
        }
    ]

    df_list = []

    # Call the function
    extract_hotel_data(df_list, hotel_data_list)

    # Assertions
    assert len(df_list) == 2

    # Ensure all DataFrames have consistent dtypes before concatenation
    expected_dtypes = {
        'Hotel': 'object',
        'Review': 'float64',
        'Price': 'float64',
        'Location': 'object'
    }
    
    for df in df_list:
        for col, dtype in expected_dtypes.items():
            assert df[col].dtype == dtype, f"Column {col} has wrong dtype: {df[col].dtype} != {dtype}"

    # Concatenate with consistent dtypes
    df = pd.concat(df_list, ignore_index=True)

    assert df.shape == (2, 4)
    assert df['Hotel'].tolist() == [None, 'Hotel B']
    assert df['Location'].tolist() == ['Osaka', None]

    # No need to convert to numeric since dtypes are already correct
    assert df['Review'].iloc[0] == 4.5
    assert np.isnan(df['Review'].iloc[1])
    assert df['Price'].iloc[0] == 150.0
    assert np.isnan(df['Price'].iloc[1])


def test_extract_hotel_data_empty_list():
    # Empty hotel data list
    hotel_data_list = []

    df_list = []

    # Call the function
    extract_hotel_data(df_list, hotel_data_list)

    # Assertions
    assert len(df_list) == 0
    assert df_list == []


def test_extract_hotel_data_basic():
    # Sample hotel data
    hotel_data_list = [
        {
            "displayName": {"text": "Hotel A"},
            "basicPropertyData": {"reviewScore": {"score": 4.5}},
            "blocks": [{"finalPrice": {"amount": 150}}],
            'location': {'displayLocation': 'Osaka'}
        },
        {
            "displayName": {"text": "Hotel B"},
            "basicPropertyData": {"reviewScore": {"score": 4.0}},
            "blocks": [{"finalPrice": {"amount": 200}}],
            'location': {'displayLocation': 'Tokyo'}
        }
    ]

    df_list = []

    # Call the function
    extract_hotel_data(df_list, hotel_data_list)

    # Assertions
    assert len(df_list) == 2

    # Ensure all DataFrames have consistent dtypes before concatenation
    expected_dtypes = {
        'Hotel': 'object',
        'Review': 'float64',
        'Price': 'float64',
        'Location': 'object'
    }
    
    for df in df_list:
        for col, dtype in expected_dtypes.items():
            assert df[col].dtype == dtype, f"Column {col} has wrong dtype: {df[col].dtype} != {dtype}"

    # Concatenate with consistent dtypes
    df = pd.concat(df_list, ignore_index=True)
    
    assert df.shape == (2, 4)
    assert df['Hotel'].tolist() == ['Hotel A', 'Hotel B']
    assert df['Review'].tolist() == [4.5, 4.0]
    assert df['Price'].tolist() == [150.0, 200.0]
    assert df['Location'].tolist() == ['Osaka', 'Tokyo']
