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

This project implements an end-to-end ETL (Extract, Transform, Load) pipeline using **Apache Airflow**, **Alpha Vantage Stock API**, and **Snowflake**.  
The goal is to automate the extraction of stock market data from Alpha Vantage, transform it into a structured format, and load it into Snowflake for analytical use.

The pipeline is orchestrated through an Airflow DAG built using the `@task` decorator for modular task design.  
Each task handles a distinct stage of the pipeline — data extraction from the API, transformation, and loading into Snowflake — with proper task dependencies ensuring reliable scheduling and execution.

Key components:

- **Alpha Vantage API** – Source of real-time and historical stock data.
- **Airflow Variables** – Used to securely store and retrieve the API key and other configurations.
- **Snowflake Connection** – Configured in Airflow to manage database interactions for data loading.
- **SQL Transactions** – Used to implement a full refresh mechanism for data consistency.
- **Airflow Web UI** – Provides DAG visualization, monitoring, and log tracking.
