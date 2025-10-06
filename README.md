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

![Image]()
