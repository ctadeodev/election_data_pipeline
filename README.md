##### Table of Contents
- [US Presidential Election Data Pipeline](#us-presidential-election-data-pipeline)
  - [Project Overview](#project-overview)
  - [Technologies Used](#technologies-used)
  - [Project Structure](#project-structure)
    - [1. Data Generation and Streaming:](#1-data-generation-and-streaming)
    - [2. Staging and Initial Processing:](#2-staging-and-initial-processing)
    - [3. Data Transformation and Loading:](#3-data-transformation-and-loading)
    - [4. Data Warehousing:](#4-data-warehousing)
    - [5. Data Visualization:](#5-data-visualization)
  - [Getting Started](#getting-started)
    - [1. Prerequisites:](#1-prerequisites)
    - [2. Setting Up Kafka and PostgreSQL:](#2-setting-up-kafka-and-postgresql)
    - [3. Running the Pipeline:](#3-running-the-pipeline)
    - [4. Orchestrating ETL with Apache Airflow:](#4-orchestrating-etl-with-apache-airflow)
    - [5. Visualizing Data with Tableau:](#5-visualizing-data-with-tableau)
  - [Directory Structure](#directory-structure)


# US Presidential Election Data Pipeline
This project aims to simulate a US presidential election data pipeline using various technologies and tools for data streaming, ETL, data warehousing, and data visualization.

## Project Overview
The project involves the following components:
1. **Data Generation**: Using the randomuser API to generate simulated voter data.
2. **Data Streaming**: Utilizing Kafka for streaming voter registration and voting events.
3. **Staging and Transformation**: Storing data in a PostgreSQL staging database and transforming it using Apache Airflow and DBT.
4. **Data Warehousing**: Loading transformed data into a data warehouse.
5. **Data Visualization**: Visualizing election results and voter turnout using Tableau.
   
## Technologies Used
* **Apache Kafka**: For data streaming and event handling.
* **PostgreSQL**: Staging database for temporary storage.
* **Apache Airflow**: Orchestration of ETL tasks.
* **DBT (Data Build Tool)**: Transforming data in the staging database.
* **Snowflake**: Cloud data warehouse for storing transformed data.
* **Tableau**: Data visualization and dashboard creation.

## Project Structure
The project is structured into several stages:

### 1. Data Generation and Streaming:
Utilizes the randomuser API to simulate voter registration.
Kafka is used to stream voter registration and voting events (registration and vote topics).

### 2. Staging and Initial Processing:
Data from Kafka is consumed and stored in a PostgreSQL staging database (election_db).
Two main tables: voters and votes, capturing voter registration details and voting events.

### 3. Data Transformation and Loading:
Apache Airflow is used to orchestrate the ETL process.
DBT is used to transform data from the staging database into star schema format suitable for the data warehouse.

### 4. Data Warehousing:
Transformed data is loaded into Snowflake, a scalable and flexible cloud data warehouse.

### 5. Data Visualization:
Tableau is employed to create visualizations and dashboards for election results, voter turnout, and other metrics.

## Getting Started
To run this project locally or in your own environment, follow these steps:

### 1. Prerequisites:
* Docker installed for running Kafka and PostgreSQL containers.  
* Python environment for running Airflow tasks.  
* Access to a cloud platform (e.g., Google Cloud, AWS) for setting up Snowflake.  

### 2. Setting Up Kafka and PostgreSQL:
* Use Docker Compose to set up Kafka and PostgreSQL containers.
* Create topics (registration and vote) in Kafka for data streaming.

### 3. Running the Pipeline:
* Start data generation and streaming using Kafka producers.
* Consume events using Kafka consumers and store them in PostgreSQL.

### 4. Orchestrating ETL with Apache Airflow:
* Define Airflow DAGs to handle data transformation tasks.
* Use DBT to transform data from PostgreSQL staging to Snowflake data warehouse.

### 5. Visualizing Data with Tableau:
* Connect Tableau to Snowflake to create visualizations and dashboards.
* Analyze election results, voter turnout, and other metrics.

## Directory Structure
```graphql
project-root/
├── dags/                 # Airflow DAGs and configurations
├── db/                      # database initialization scripts
├── dbt/                     # DBT models and transformations
├── docker-compose.yml       # Docker configuration for Kafka and PostgreSQL
│   ├── models/
│   ├── dbt_project.yml
│   └── profiles.yml
├── README.md                # Project overview, setup instructions, and usage guide
└── scripts/                 # Scripts for data generation, Kafka producers/consumers
```
