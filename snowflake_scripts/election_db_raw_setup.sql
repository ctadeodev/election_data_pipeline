use role accountadmin;
create role if not exists dbt_role;
grant role dbt_role to user mjmendez;

create warehouse if not exists election_wh with warehouse_size='x-small';
create database if not exists election_db_raw;
grant usage on warehouse election_wh to role dbt_role;
grant all on database election_db_raw to role dbt_role;

use role dbt_role;
create schema if not exists election_db_raw.election_schema;

USE WAREHOUSE election_wh;
USE database election_db_raw;
USE SCHEMA election_schema;

CREATE TABLE IF NOT EXISTS voters (
    voter_id INTEGER PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    gender CHAR(1) NOT NULL,
    registration_date TIMESTAMP_NTZ NOT NULL,
    state VARCHAR(2),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
CREATE TABLE IF NOT EXISTS elections (
    election_id INTEGER PRIMARY KEY,
    election_name VARCHAR(255) NOT NULL,
    election_date DATE NOT NULL,
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INTEGER PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    party VARCHAR(100),
    election_id INT NOT NULL,
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (election_id) REFERENCES elections (election_id)
);
CREATE TABLE IF NOT EXISTS votes (
    vote_id INTEGER PRIMARY KEY,
    voter_id INT NOT NULL,
    candidate_id INT NOT NULL,
    election_id INT NOT NULL,
    vote_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (voter_id) REFERENCES voters (voter_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
    FOREIGN KEY (election_id) REFERENCES elections (election_id),
    CONSTRAINT unique_vote_per_election UNIQUE (voter_id, election_id)
);