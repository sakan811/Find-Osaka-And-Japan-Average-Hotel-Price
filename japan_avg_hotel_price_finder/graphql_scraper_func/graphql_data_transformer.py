import datetime

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')


def transform_data_in_df(check_in, city, dataframe) -> pd.DataFrame:
    """
    Transform data in DataFrame.
    :param check_in: Check-in date.
    :param city: City where the hotels are located.
    :param dataframe: Pandas DataFrame to be transformed.
    :return: Pandas DataFrame.
    """
    if not dataframe.empty:
        logger.info("Add City column to DataFrame")
        dataframe['City'] = city
        logger.info("Add Date column to DataFrame")
        dataframe['Date'] = check_in
        logger.info("Add AsOf column to DataFrame")
        dataframe['AsOf'] = datetime.datetime.now()

        logger.info("Remove duplicate rows from the DataFrame based on 'Hotel' column")
        df_filtered = dataframe.drop_duplicates(subset='Hotel').copy()

        logger.info("Convert columns to numeric values")
        df_filtered.loc[:, 'Price'] = pd.to_numeric(df_filtered['Price'], errors='coerce')
        df_filtered.loc[:, 'Review'] = pd.to_numeric(df_filtered['Review'], errors='coerce')

        # Drop rows where any of the 'Hotel', 'Review', 'Price' columns are None or NaN
        logger.info("Dropping rows where 'Hotel', 'Review', or 'Price' columns are None or NaN")
        df_filtered = df_filtered.dropna(subset=['Hotel', 'Review', 'Price'])

        logger.info("Dropping rows where 'Review', or 'Price' columns are 0")
        df_filtered = df_filtered[(df_filtered['Price'] != 0) & (df_filtered['Review'] != 0)]

        logger.info("Calculate the Price/Review ratio")
        df_filtered.loc[:, 'Price/Review'] = df_filtered['Price'] / df_filtered['Review']
        return df_filtered
    else:
        logger.warning("Dataframe is empty. No data was scraped.")
        return dataframe
