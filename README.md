# ETL Pipeline for Alpha Vantage Stock Data with Snowflake and Apache Airflow

## Project Overview

The goal of this project is to automate the extraction of stock market data from Alpha Vantage, transform it into a structured format, and load it into Snowflake for analytical use.

The pipeline is orchestrated through an Airflow DAG built using the `@task` decorator for modular task design.  
Each task handles a distinct stage of the pipeline — data extraction from the API, transformation, and loading into Snowflake — with proper task dependencies ensuring reliable scheduling and execution.

## Architecture and Technologies

The ETL pipeline follows a modular architecture with Airflow as the orchestration layer.  
Data flows from **Alpha Vantage API → Airflow Tasks → Snowflake Data Warehouse**.

**Core Technologies:**

- **Apache Airflow:** Workflow orchestration, task scheduling, and dependency management.
- **Alpha Vantage API:** Provides stock market data (JSON/CSV) via REST API.
- **Snowflake:** Cloud-based data warehouse for structured data storage and analytics.
- **Python:** Core language for task logic and data transformation.
- **Airflow Variables & Connections:** Securely manage credentials (API key, Snowflake credentials).

**Data Flow Summary:**

1. Extract stock data from Alpha Vantage using API requests.
2. Transform and clean the dataset within Airflow tasks.
3. Load the processed data into a Snowflake table using a transactional full refresh.

## Setup Instruction

### Environment Setup

1. Install Python >= 3.9 and Apache Airflow via Docker Compose by the following command below:

```bash
docker compose -f ./docker-compose.yaml up airflow-init
docker compose -f ./docker-compose.yaml up
```

#### Apache Airflow with Docker Compose

This setup provides a local development environment for Apache Airflow using Docker Compose.
It runs Airflow with **LocalExecutor, PostgreSQL**, and the Airflow webserver and scheduler.

`docker compose up airflow-init`

This command runs only the initialization container (`airflow-init`) to setup Airflow's environment before the main services start

**What it does**

- Waits for Postgres to start session
- Checks Docker Resources (CPU, memory, disk).
- Creates required folders and sets correct permissions:

```bash
./log # Airflow logs
./dags # DAG Files
./plugins # Custom Airflow plugins
./config # Optional custom configs
```

- Runs Airflow initialization steps:
  - Executes **database migrations**.
  - Creates the default admin user:
    - Username: `airflow`
    - Password: `airflow`

## Alpha Vantage API Configuration

### Setting Airflow Variable for API Key

1. In Airflow UI -> Admin -> Variables, create a variable:
   - Key: `alpha_vantage_api`
   - Value: your actual API Key [Go to https://www.alphavantage.co/]

### Using the Variable in Code

Retrieve the key in your task:

```python
from airflow.models import Variable
api_key = Variable.get("alpha_vantage_api")
```

### Admin Variables Screenshot

![Image](https://raw.githubusercontent.com/aakashvardhan/aakash-airflow-snowflake-dag/main/screenshots/list-variable-airflow.png)

## Snowflake Connection Setup

### Creating Snowflake Connections in Airflow

1. Go to Admin -> Connections in Airflow.
2. Create a new connection:
   - **Conn ID**: `my_snowflake_conn`
   - **Conn Type**: Snowflake
   - **Account, User, Password, Warehouse, Database, Schema** -> fill as per your setup

### Using the Connection in the DAG

```python
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
hook = SnowflakeHook(snowflake_conn_id="my_snowflake_conn")
```

### Connection Details Screenshot

![image](https://raw.githubusercontent.com/aakashvardhan/aakash-airflow-snowflake-dag/main/screenshots/connection-credential.png)

![image](https://raw.githubusercontent.com/aakashvardhan/aakash-airflow-snowflake-dag/main/screenshots/airflow-connection-settings.png)

## Airflow DAG Implementation

### DAG Overview

The DAG (Directed Acyclic Graph) is designed for clarity, modularity, and fault tolerance. Each step is represented as a task function with clear dependencies.

### Tasks using `@task` Decorator

```python
from airflow.decorators import task

@task
def extract_90_days_stock_data(symbol: str):
    # Fetch 90 days of stock data from Alpha Vantage
    ...

@task
def transform(price_list, symbol):
    # Transform the data structure from dict to list of lists
    ...

@task
def load_v2(records, symbol):
    # Insert into Snowflake using connection
    # Implement Full Refresh Transaction
    ...
```

### Tasks Dependencies and Scheduling

Tasks are linked in the DAG definition:

```python
extract_90_days_stock_data() >> transform() >> load_v2()
```

## Full Refresh with SQL Transaction

Load = "Full Refresh" via transaction

- `load_v2(records, symbol)` (Airflow `@task`) opens a Snowflake cursor and wraps everything in a transaction:
  - `BEGIN;`
  - `CREATE OR REPLACE TABLE {DATABASE}.RAW.{symbol}_stock_price (...) PRIMARY KEY (symbol, date)`
    - `OR REPLACE` drops/recreates the table atomically, which is the foundation of full refresh (where old data is being replaced).
  - Iterates `records` and executes `INSERT` per row.
  - `COMMIT;` on success; `ROLLBACK;` on any error; cursor closed in `finally`

## Execution and Validation

### Airflow Homepage Screenshot

![image](https://raw.githubusercontent.com/aakashvardhan/aakash-airflow-snowflake-dag/main/screenshots/triggered-dag.png)

### DAG Log Screenshot

#### DAG Graph

![image](https://raw.githubusercontent.com/aakashvardhan/aakash-airflow-snowflake-dag/main/screenshots/airflow-dag-graph.png)

#### Event Logs

![image](https://raw.githubusercontent.com/aakashvardhan/aakash-airflow-snowflake-dag/main/screenshots/event-log.png)

## References and Resources

- [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Snowflake Documentation](https://docs.snowflake.com/)
