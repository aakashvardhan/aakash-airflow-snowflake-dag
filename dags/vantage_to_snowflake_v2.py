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
        "outputsize": "compact",
    }
    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    # get only last 90 days of data
    if "Time Series (Daily)" not in data:
        raise ValueError(f"Error fetching data for symbol {symbol}: {data}")
    if len(data["Time Series (Daily)"]) > 90:
        data["Time Series (Daily)"] = dict(
            list(data["Time Series (Daily)"].items())[:90]
        )
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
        # load records
        for r in records:
            _symbol = r[0].replace("'", "''")
            _date = r[1].replace("'", "''")
            _open = r[2].replace("'", "''")
            _close = r[3].replace("'", "''")
            _high = r[4].replace("'", "''")
            _low = r[5].replace("'", "''")
            _volume = r[6].replace("'", "''")

            sql = f"""
                INSERT INTO {target_table} (symbol, date, open, close, high, low, volume)
                VALUES ('{_symbol}', '{_date}', {_open}, {_close}, {_high}, {_low}, {_volume})
            """
            # print(sql)
            con.execute(sql)
        con.execute("COMMIT;")
    except Exception as e:
        con.execute("ROLLBACK;")
        print(e)
        raise e
    finally:
        con.close()


@task
def check_table_stats(table):
    conn = return_snowflake_hook()
    conn.execute(f"SELECT * FROM {table} LIMIT 5;")
    df = conn.fetch_pandas_all()
    print(df.head())
    print(len(df))


with DAG(
    dag_id="vantage_to_snowflake_v2",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["ETL"],
    schedule=None,
) as dag:

    symbols = "TSLA"
    target_table = f"{DATABASE}.raw.{symbols}_stock_price"

    extracted_data_2 = extract_90_days_stock_data(symbols)
    transformed_data_2 = transform(extracted_data_2, symbols)
    load_v2(transformed_data_2, symbols)
