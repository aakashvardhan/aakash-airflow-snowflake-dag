# ETL Pipeline for Alpha Vantage Stock Data with Snowflake and Apache Airflow

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture and Technologies](#architecture-and-technologies)
3. [Setup Instructions](#setup-instructions)
   - [Environment Setup](#environment-setup)
   - [Installing Dependencies](#installing-dependencies)
4. [Alpha Vantage API Configuration](#alpha-vantage-api-configuration)
   - [Setting Airflow Variable for API Key](#setting-airflow-variable-for-api-key)
   - [Using the Variable in Code](#using-the-variable-in-code)
   - [Admin Variables Screenshot (①)](#admin-variables-screenshot-①)
5. [Snowflake Connection Setup](#snowflake-connection-setup)
   - [Creating Snowflake Connection in Airflow](#creating-snowflake-connection-in-airflow)
   - [Using the Connection in the DAG](#using-the-connection-in-the-dag)
   - [Connection Details Screenshot (②)](#connection-details-screenshot-②)
6. [Airflow DAG Implementation](#airflow-dag-implementation)
   - [DAG Overview](#dag-overview)
   - [Tasks Using `@task` Decorator](#tasks-using-task-decorator)
   - [Task Dependencies and Scheduling](#task-dependencies-and-scheduling)
7. [Full Refresh with SQL Transaction](#full-refresh-with-sql-transaction)
8. [Execution and Validation](#execution-and-validation)
   - [Airflow Homepage Screenshot (③)](#airflow-homepage-screenshot-③)
   - [DAG Log Screenshot (④)](#dag-log-screenshot-④)
9. [Results and Observations](#results-and-observations)

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
