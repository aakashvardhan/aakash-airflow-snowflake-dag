from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

from datetime import datetime, timedelta
import snowflake.connector
import requests
import json

USER_ID = Variable.get("snowflake_userid")
ACCOUNT = Variable.get("snowflake_account")
DATABASE = Variable.get("snowflake_database")
PASSWORD = Variable.get("snowflake_password")
ALPHA_VANTAGE_API_KEY = Variable.get("alpha_vantage_api")
VWH = Variable.get("snowflake_vwh")


def return_snowflake_hook():
    hook = SnowflakeHook(snowflake_conn_id="my_snowflake_conn")
    conn = hook.get_conn()
    return conn.cursor()


def get_stock_data(symbol, api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": 90,
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data


@task
def extract_90_days_stock_data(symbol: str):
    _stock_data = get_stock_data(symbol, ALPHA_VANTAGE_API_KEY)

    # storing 90 days of stock info (open, high, low, close, volume)
    results = []

    for d, daily_data in _stock_data["Time Series (Daily)"].items():
        stock_info = _stock_data["Time Series (Daily)"][d]
        stock_info["date"] = d
        results.append(stock_info)
    return results


@task
def transform(price_list, symbol):
    transformed_list = []
    for price in price_list:
        transformed_list.append(
            [
                symbol,
                price["date"],
                price["1. open"],
                price["4. close"],
                price["2. high"],
                price["3. low"],
                price["5. volume"],
            ]
        )
    return transformed_list


@task
def load_v2(records, symbol):
    con = return_snowflake_hook()

    staging_table = f"{DATABASE}.raw.temp_{symbol}_stock_price"
    target_table = f"{DATABASE}.raw.{symbol}_stock_price"
    try:
        con.execute("BEGIN;")
        con.execute(
            f"""
                -- CREATE TABLE IF NOT EXISTS {target_table} (
                        CREATE OR REPLACE TABLE {target_table} (

                            symbol VARCHAR(10),
                            date DATE,
                            open FLOAT,
                            close FLOAT,
                            high FLOAT,
                            low FLOAT,
                            volume FLOAT,
                            PRIMARY KEY (symbol, date)
                    );"""
        )
        con.execute(
            f"""

                    CREATE OR REPLACE TABLE {staging_table} (
                        symbol VARCHAR(10),
                        date DATE,
                        open FLOAT,
                        close FLOAT,
                        high FLOAT,
                        low FLOAT,
                        volume FLOAT,
                        PRIMARY KEY (symbol, date)
                    );"""
        )
        # load records
        for r in records:
            _symbol = r[0].replace("'", "''")
            _date = r[1].replace("'", "''")
            _open = r[2].replace("'", "''")
            _close = r[3].replace("'", "''")
            _high = r[4].replace("'", "''")
            _low = r[5].replace("'", "''")
            _volume = r[6].replace("'", "''")
            print(
                _symbol,
                "-",
                _date,
                "-",
                _open,
                "-",
                _close,
                "-",
                _high,
                "-",
                _low,
                "-",
                _volume,
            )

            sql = f"""
                INSERT INTO {target_table} (symbol, date, open, close, high, low, volume)
                VALUES ('{_symbol}', '{_date}', {_open}, {_close}, {_high}, {_low}, {_volume})
            """
            # print(sql)
            con.execute(sql)
        con.execute("COMMIT;")

        # performing upsert -> incremental update
        upsert_sql = f"""
            -- Performing upsert
            MERGE INTO {target_table} AS target
            USING {staging_table} AS source
            ON target.symbol = source.symbol AND target.date = source.date
            WHEN MATCHED THEN
                UPDATE SET
                    target.symbol = source.symbol,
                    target.date = source.date,
                    target.open = source.open,
                    target.close = source.close,
                    target.high = source.high,
                    target.low = source.low,
                    target.volume = source.volume
            WHEN NOT MATCHED THEN
                INSERT (symbol, date, open, close, high, low, volume)
                VALUES (source.symbol, source.date, source.open, source.close, source.high, source.low, source.volume);
        """
        con.execute(upsert_sql)
    except Exception as e:
        con.execute("ROLLBACK;")
        print(e)
        raise e


with DAG(
    dag_id="vantage_to_snowflake_v2",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["ETL"],
    schedule="30 2 * * *",
) as dag:

    symbols = "AAPL"

    extracted_data = extract_90_days_stock_data(symbols)
    transformed_data = transform(extracted_data, symbols)
    load_v2(transformed_data, symbols)
