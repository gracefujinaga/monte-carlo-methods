import psycopg2
import random
import time
import psutil
import os
import pandas as pd

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

    process = psutil.Process(os.getpid())
    memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB

    query = f"SELECT ID FROM logs"
    cursor.execute(query)
    rows = cursor.fetchall()
    ids = [x[0] for x in rows]

    ids = random.sample(ids, num_incidents)

    for incident_id in ids: 
        query = f"SELECT * FROM logs WHERE ID = '{incident_id}'"
        cursor.execute(query)
        rows = cursor.fetchall()

    memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB

    cursor.close()
    conn.close()
    return memory_after_fetch - memory_before_query


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
    #print(f"Memory before query: {memory_before_query:.2f} MB")

    for incident_id in ids:
        # SQL query to update the incident_state to 'Resolved'
        query= f"""
        UPDATE logs
        SET incident_state = 'Resolved', active = FALSE
        WHERE ID = '{incident_id}'
        """
        cursor.execute(query)  # Execute the update query

    memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB
    #print(f"Memory after fetch: {memory_after_fetch:.2f} MB")

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return memory_after_fetch - memory_before_query

def generate_incident():
    # generate number field
    random_number = random.randint(0, 9999999)
    incident_number = f"INC{random_number:07}"  # Formats with leading zeros if needed

    # generate state
    states = [
        'New', 'Resolved', 'Closed', 'Active', 'Awaiting User Info',
        'Awaiting Problem', 'Awaiting Vendor', 'Awaiting Evidence', '-100'
    ]
    state = random.choice(states)

    # generate active
    active = random.choice([True, False])

    # generate reassignment
    reassignment = random.randint(0, 27)

    # generate sys mod count
    sys_mod = random.randint(0, 20)

    # caller id
    caller = f"Caller {random.randint(1000, 9999)}"

    return incident_number, state, active, reassignment, sys_mod, caller

def insert(num_incidents):
    # get a list of the current ids in the database
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # get a list of incidents
    incident_list = [generate_incident() for _ in range(num_incidents)]

    process = psutil.Process(os.getpid())
    memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB

    for incident in incident_list:
        query = f"""
            INSERT INTO logs (number, incident_state, active, reassignment_count, sys_mod_count, caller_id)
            VALUES ('{incident[0]}', '{incident[1]}', {incident[2]}, '{incident[3]}', '{incident[4]}', '{incident[5]}')
            """
        cursor.execute(query)


    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # start measuring memory
    memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB

    return memory_after_fetch - memory_before_query


# Function to measure memory and time
def measure_postgresql_query(func, num_incidents):

    # Measure memory and time usage
    #process = psutil.Process(os.getpid())
    # memory_before = process.memory_info().rss / 1024 / 1024  # in MB
    start_time = time.time()

    mem_usage = func(num_incidents)

    end_time = time.time()
    # memory_after = process.memory_info().rss / 1024 / 1024  # in MB

    time_taken = end_time - start_time
    memory_used = mem_usage

    print(f"PostgreSQL {func.__name__} - Time: {time_taken:.4f} seconds, Memory Used: {memory_used} MB")

# Example of running for 10, 100, 1000 incidents
for count in [10, 100, 1000]:
    print(f"--------------------{count}-----------------------")
    measure_postgresql_query(read, count)
    measure_postgresql_query(update, count)
    measure_postgresql_query(insert, count)