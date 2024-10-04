import sqlite3

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import main_logger


def migrate_data_to_sqlite(df_filtered: pd.DataFrame, db: str) -> None:
    """
    Migrate hotel data to sqlite database.
    :param df_filtered: pandas dataframe.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info('Connecting to SQLite database (or create it if it doesn\'t exist)...')

    with sqlite3.connect(db) as con:
        query = '''
        CREATE TABLE IF NOT EXISTS HotelPrice (
            ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Hotel TEXT NOT NULL,
            Price REAL NOT NULL,
            Review REAL NOT NULL,
            Location TEXT NOT NULL,
            "Price/Review" REAL NOT NULL,
            City TEXT NOT NULL,
            Date TEXT NOT NULL,
            AsOf TEXT NOT NULL
        )
        '''

        con.execute(query)

        hotel_price_dtype: dict = get_hotel_price_dtype()

        # Save the DataFrame to a table named 'HotelPrice'
        df_filtered.to_sql('HotelPrice', con=con, if_exists='append', index=False, dtype=hotel_price_dtype)

        con.commit()

        main_logger.info(f'Data has been saved to {db}')

        create_avg_hotel_room_price_by_date_table(db)

        create_avg_room_price_by_review_table(db)

        create_avg_hotel_price_by_dow_table(db)

        create_avg_hotel_price_by_month_table(db)

        create_avg_room_price_by_location(db)


def get_hotel_price_dtype() -> dict:
    """
    Get HotelPrice datatype.
    :return: HotelPrice datatype.
    """
    main_logger.info('Get HotelPrice datatype...')
    hotel_price_dtype = {
        'Hotel': 'text not null primary key',
        'Price': 'real not null',
        'Review': 'real not null',
        'Location': 'text not null',
        'Price/Review': 'real not null',
        'City': 'text not null',
        'Date': 'text not null',
        'AsOf': 'text not null'
    }
    return hotel_price_dtype


def create_avg_hotel_room_price_by_date_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByDate table
    :param db: SQLite database path
    :return: None
    """
    main_logger.info('Create AverageRoomPriceByDate table...')
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageRoomPriceByDateTable (
            Date TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            City TEXT NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageRoomPriceByDateTable 
        '''
        con.execute(query)

        query = '''
        insert into AverageRoomPriceByDateTable (Date, AveragePrice, City)
        SELECT
            Date,
            AVG(Price) AS IQMPrice,
            City
        FROM (
            SELECT
                Date,
                Price,
                NTILE(4) OVER (PARTITION BY Review ORDER BY Price) AS Quartile,
                City
            FROM HotelPrice
        )
        WHERE Quartile IN (2, 3)
        GROUP BY Date;
        '''
        con.execute(query)


def create_avg_room_price_by_review_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByReview table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByReview table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByReview (
            Review REAL NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByReview 
        '''
        con.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByReview (Review, AveragePrice)
        SELECT
            Review,
            AVG(Price) AS IQMPrice
        FROM (
            SELECT
                Review,
                Price,
                NTILE(4) OVER (PARTITION BY Review ORDER BY Price) AS Quartile
            FROM HotelPrice
        )
        WHERE Quartile IN (2, 3)
        GROUP BY Review;
        '''
        con.execute(query)


def create_avg_hotel_price_by_dow_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByDayOfWeek table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByDayOfWeek table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByDayOfWeek (
            DayOfWeek TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByDayOfWeek 
        '''
        con.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByDayOfWeek (DayOfWeek, AveragePrice)
        WITH PricedDays AS (
            SELECT
                CASE strftime('%w', Date)
                    WHEN '0' THEN 'Sunday'
                    WHEN '1' THEN 'Monday'
                    WHEN '2' THEN 'Tuesday'
                    WHEN '3' THEN 'Wednesday'
                    WHEN '4' THEN 'Thursday'
                    WHEN '5' THEN 'Friday'
                    WHEN '6' THEN 'Saturday'
                END AS day_of_week,
                Price,
                NTILE(4) OVER (
                    PARTITION BY strftime('%w', Date)
                    ORDER BY Price
                ) AS quartile
            FROM
                HotelPrice
        )
        SELECT
            day_of_week,
            AVG(Price) AS iqm_price
        FROM
            PricedDays
        WHERE
            quartile IN (2, 3)
        GROUP BY
            day_of_week
        ORDER BY
            CASE day_of_week
                WHEN 'Sunday' THEN 1
                WHEN 'Monday' THEN 2
                WHEN 'Tuesday' THEN 3
                WHEN 'Wednesday' THEN 4
                WHEN 'Thursday' THEN 5
                WHEN 'Friday' THEN 6
                WHEN 'Saturday' THEN 7
            END;
        '''
        con.execute(query)


def create_avg_hotel_price_by_month_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByMonth table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByMonth table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByMonth (
            Month TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            Quarter TEXT NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByMonth 
        '''
        con.execute(query)

        query = '''
        WITH MonthlyPrices AS (
            SELECT
                CASE strftime('%m', Date)
                    WHEN '01' THEN 'January'
                    WHEN '02' THEN 'February'
                    WHEN '03' THEN 'March'
                    WHEN '04' THEN 'April'
                    WHEN '05' THEN 'May'
                    WHEN '06' THEN 'June'
                    WHEN '07' THEN 'July'
                    WHEN '08' THEN 'August'
                    WHEN '09' THEN 'September'
                    WHEN '10' THEN 'October'
                    WHEN '11' THEN 'November'
                    WHEN '12' THEN 'December'
                END AS month,
                Price,
                CASE
                    WHEN strftime('%m', Date) IN ('01', '02', '03') THEN 'Quarter1'
                    WHEN strftime('%m', Date) IN ('04', '05', '06') THEN 'Quarter2'
                    WHEN strftime('%m', Date) IN ('07', '08', '09') THEN 'Quarter3'
                    WHEN strftime('%m', Date) IN ('10', '11', '12') THEN 'Quarter4'
                END AS quarter,
                NTILE(4) OVER (
                    PARTITION BY strftime('%m', Date)
                    ORDER BY Price
                ) AS quartile
            FROM
                HotelPrice
        )
        INSERT INTO AverageHotelRoomPriceByMonth (Month, AveragePrice, Quarter)
        SELECT
            month,
            AVG(Price) AS iqm_price,
            quarter
        FROM
            MonthlyPrices
        WHERE
            quartile IN (2, 3)
        GROUP BY
            month
        ORDER BY
            CASE month
                WHEN 'January' THEN 1
                WHEN 'February' THEN 2
                WHEN 'March' THEN 3
                WHEN 'April' THEN 4
                WHEN 'May' THEN 5
                WHEN 'June' THEN 6
                WHEN 'July' THEN 7
                WHEN 'August' THEN 8
                WHEN 'September' THEN 9
                WHEN 'October' THEN 10
                WHEN 'November' THEN 11
                WHEN 'December' THEN 12
            END;
        '''
        con.execute(query)


def create_avg_room_price_by_location(db: str) -> None:
    """
    Create AverageHotelRoomPriceByLocation table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByLocation table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByLocation (
            Location TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            AverageRating REAL NOT NULL,
            AveragePricePerReview REAL NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByLocation
        '''
        con.execute(query)

        query = '''
        WITH LocationMetrics AS (
            SELECT
                Location,
                Price,
                Review,
                "Price/Review",
                NTILE(4) OVER (PARTITION BY Location ORDER BY Price) AS price_quartile,
                NTILE(4) OVER (PARTITION BY Location ORDER BY Review) AS review_quartile,
                NTILE(4) OVER (PARTITION BY Location ORDER BY "Price/Review") AS price_per_review_quartile
            FROM HotelPrice
        )
        INSERT INTO AverageHotelRoomPriceByLocation (Location, AveragePrice, AverageRating, AveragePricePerReview)
        SELECT
            Location,
            COALESCE(AVG(CASE WHEN price_quartile IN (2, 3) THEN Price END), 0) AS IQM_Price,
            COALESCE(AVG(CASE WHEN review_quartile IN (2, 3) THEN Review END), 0) AS IQM_Rating,
            COALESCE(AVG(CASE WHEN price_per_review_quartile IN (2, 3) THEN "Price/Review" END), 0) AS IQM_PricePerReview
        FROM LocationMetrics
        GROUP BY Location;
        '''
        con.execute(query)


if __name__ == '__main__':
    pass
