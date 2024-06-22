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

    CREATE TABLE voters (
        voter_id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        dob DATE NOT NULL,
        gender CHAR(1) NOT NULL,
        registration_date TIMESTAMP NOT NULL,
        state VARCHAR(2),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE elections (
        election_id SERIAL PRIMARY KEY,
        election_name VARCHAR(255) NOT NULL,
        election_date DATE NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE candidates (
        candidate_id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        party VARCHAR(100),
        election_id INT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (election_id) REFERENCES elections (election_id)
    );

    CREATE TABLE votes (
        vote_id SERIAL PRIMARY KEY,
        voter_id INT NOT NULL,
        candidate_id INT NOT NULL,
        election_id INT NOT NULL,
        vote_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (voter_id) REFERENCES voters (voter_id),
        FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
        FOREIGN KEY (election_id) REFERENCES elections (election_id),
        CONSTRAINT unique_vote_per_election UNIQUE (voter_id, election_id)
    );

    CREATE TABLE last_pull_info (
        table_name VARCHAR(255) PRIMARY KEY,
        last_pull_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create trigger function
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS \$$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    \$$ LANGUAGE plpgsql;

    -- Create triggers
    CREATE TRIGGER update_candidates_updated_at
    BEFORE UPDATE ON candidates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_elections_updated_at
    BEFORE UPDATE ON elections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_voters_updated_at
    BEFORE UPDATE ON voters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_votes_updated_at
    BEFORE UPDATE ON votes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    INSERT INTO last_pull_info (table_name) VALUES 
        ('voters'),
        ('elections'),
        ('candidates'),
        ('votes');

    INSERT INTO elections (election_name, election_date) VALUES
        ('Presidential Election 2024', '2024-11-05');

    INSERT INTO candidates (full_name, party, election_id) VALUES
        ('Abraham Lincoln', 'Republican', 1),
        ('Franklin D. Roosevelt', 'Democratic', 1),
        ('George Washington', 'Federalist', 1);
EOSQL

echo "Database initialization complete."
