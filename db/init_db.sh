#!/bin/bash

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Create election_db database
echo "Creating election_db database..."
PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres <<-EOSQL
    CREATE DATABASE election_db;
EOSQL

# Connect to election_db and create tables
echo "Creating tables in election_db..."
PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d election_db <<-EOSQL
    CREATE TABLE candidates (
        candidate_id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        party VARCHAR(100),
        election_id INT NOT NULL
    );

    CREATE TABLE elections (
        election_id SERIAL PRIMARY KEY,
        election_name VARCHAR(255) NOT NULL,
        election_date DATE NOT NULL
    );

    CREATE TABLE voters (
        voter_id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        dob DATE NOT NULL,
        gender CHAR(1) NOT NULL,
        registration_date TIMESTAMP NOT NULL,
        state VARCHAR(2)
    );

    CREATE TABLE votes (
        vote_id SERIAL PRIMARY KEY,
        voter_id INT NOT NULL,
        candidate_id INT NOT NULL,
        election_id INT NOT NULL,
        vote_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (voter_id) REFERENCES voters (voter_id),
        FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
        FOREIGN KEY (election_id) REFERENCES elections (election_id),
        CONSTRAINT unique_vote_per_election UNIQUE (voter_id, election_id)
    );
EOSQL

echo "Database initialization complete."
