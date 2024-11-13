import psycopg2
import random
import time
import psutil
import os
import pandas as pd

# TODO: FIX THE MEMORY PARTS!!!!



# Database connection details
db_config = {
    'dbname':'monte_carlo_db',
    'user': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Function to fetch incident data from PostgreSQL
def read(num_incidents):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    query = f"SELECT ID FROM logs"
    cursor.execute(query)
    rows = cursor.fetchall()
    ids = [x[0] for x in rows]

    ids = random.sample(ids, num_incidents)

    for incident_id in ids: 
        query = f"SELECT * FROM logs WHERE ID = '{incident_id}'"
        cursor.execute(query)
        rows = cursor.fetchall()

    cursor.close()
    conn.close()


def update(num_incidents):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    query = f"SELECT ID FROM logs"
    cursor.execute(query)
    rows = cursor.fetchall()
    ids = [x[0] for x in rows]

    ids = random.sample(ids, num_incidents)

    process = psutil.Process(os.getpid())
    memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB
    print(f"Memory before query: {memory_before_query:.2f} MB")


    for incident_id in ids:
        # SQL query to update the incident_state to 'Resolved'
        query= f"""
        UPDATE logs
        SET incident_state = 'Resolved', active = FALSE
        WHERE ID = '{incident_id}'
        """
        cursor.execute(query)  # Execute the update query
    memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB
    print(f"Memory after fetch: {memory_after_fetch:.2f} MB")

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return memory_after_fetch - memory_before_query


# def insert(num_incidents):
#     # get a list of the current ids in the database
#     conn = psycopg2.connect(**db_config)
#     cursor = conn.cursor()

#     query = f"""
#         INSERT INTO logs (number, incident_state, active, date, location)
#         VALUES ('{incident_number}', '{incident_state}', {active}, '{date}', '{location}')
#         """
#         cursor.execute(query)


#     # generate a new list to insert

#     # generate a random set of attributes for the insert

#     # start measuring memory
#     process = psutil.Process(os.getpid())
#     memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB
#     print(f"Memory before query: {memory_before_query:.2f} MB")



# def insert(incident_ids):
#     process = psutil.Process(os.getpid())
#     memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB
#     print(f"Memory before query: {memory_before_query:.2f} MB")

#     # Establish connection to PostgreSQL
#     conn = psycopg2.connect(**db_config)
#     cursor = conn.cursor()

#     for incident_id in incident_ids:
#         incident_number = generate_incident_number()  # Generate a new incident number
#         incident_state, active, date, location = generate_random_incident_data()  # Generate random data

#         # SQL query to insert a new incident
#         query = f"""
#         INSERT INTO logs (number, incident_state, active, date, location)
#         VALUES ('{incident_number}', '{incident_state}', {active}, '{date}', '{location}')
#         """
#         cursor.execute(query)  # Execute the insert query

#     memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB
#     print(f"Memory after fetch: {memory_after_fetch:.2f} MB")

#     # Commit the changes to the database
#     conn.commit()

#     # Close the cursor and connection
#     cursor.close()
#     conn.close()

#     return memory_after_fetch - memory_before_query



# Function to measure memory and time
def measure_postgresql_query(func, num_incidents):

    # Measure memory and time usage
    #process = psutil.Process(os.getpid())
    # memory_before = process.memory_info().rss / 1024 / 1024  # in MB
    start_time = time.time()

    mem_usage = func(num_incidents)
    print(mem_usage)

    end_time = time.time()
    # memory_after = process.memory_info().rss / 1024 / 1024  # in MB

    time_taken = end_time - start_time
    memory_used = mem_usage

    print(f"PostgreSQL {func.__name__} - Time: {time_taken:.4f} seconds, Memory Used: {memory_used} MB")

# Example of running for 10, 100, 1000 incidents
for count in [10, 100, 1000]:
    print(f"{count}:")
    #measure_postgresql_query(read, count)
    measure_postgresql_query(update, count)