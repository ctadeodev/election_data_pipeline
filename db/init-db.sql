-- Create candidates table
CREATE TABLE candidates (
    candidate_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    party VARCHAR(100),
    election_id INT NOT NULL
);

-- Create elections table
CREATE TABLE elections (
    election_id SERIAL PRIMARY KEY,
    election_name VARCHAR(255) NOT NULL,
    election_date DATE NOT NULL
);


-- Create voters table
CREATE TABLE voters (
    voter_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    gender CHAR(1) NOT NULL,
    registration_date TIMESTAMP NOT NULL,
    state VARCHAR(2)
);

-- Create votes table
CREATE TABLE votes (
    vote_id SERIAL PRIMARY KEY,
    voter_id INT NOT NULL,
    candidate_id INT NOT NULL,
    election_id INT NOT NULL,
    vote_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES voters (voter_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
    FOREIGN KEY (election_id) REFERENCES elections (election_id)
);

-- Insert sample data for candidates
INSERT INTO candidates (full_name, party, election_id) VALUES
    ('Abraham Lincoln', 'Republican', 1),
    ('Franklin D. Roosevelt', 'Democratic', 1);

-- Insert sample data for elections
INSERT INTO elections (election_name, election_date) VALUES
    ('Presidential Election 2024', '2024-11-05');
