DROP DATABASE IF EXISTS monte_carlo_db;
CREATE DATABASE monte_carlo_db;

DROP TABLE IF EXISTS logs;

\c monte_carlo_db;

CREATE TABLE logs (
     ID SERIAL, -- there are multiple numbers so we have issues with that as a primary key
     number VARCHAR(100),
     incident_state VARCHAR(100),
     active BOOLEAN,
     reassignment_count INT,
     sys_mod_count INT,
     caller_id TEXT
);

-- Copy data from CSV file into the table
COPY logs(number, incident_state, active, reassignment_count, sys_mod_count, caller_id)
FROM '/Users/gracefujinaga/Documents/Northwestern/MSDS_460/monte-carlo-methods/Data/cleaned_log_data.csv'
DELIMITER ','  
CSV HEADER;