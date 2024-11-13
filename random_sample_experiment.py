import psycopg2
import random
import time
import psutil
import os
from pymongo import MongoClient
from collections import Counter
import matplotlib.pyplot as plt

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


def postgres_exp (num_incidents) :
    # Database connection details
    db_config = {
        'dbname':'monte_carlo_db',
        'user': 'postgres',
        'host': 'localhost',
        'port': '5432'
    }

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # get the list of all ids
    query = f"SELECT ID FROM logs"
    cursor.execute(query)
    rows = cursor.fetchall()
    ids = [x[0] for x in rows]
    
    # ------------- randomly select incidents ---------------
    # Define the possible incident types and their distribution
    incident_types = ['r', 'u', 'i']
    weights = [0.8, 0.1, 0.1]  # 80% reason, 10% update, 10% insert

    # Generate a list of 100 incidents based on the specified weights
    incidents = random.choices(incident_types, weights, k=100)

    incident_types = ['r', 'u', 'i']
    weights = [0.8, 0.1, 0.1]  # 80% reason, 10% update, 10% insert

    incidents = random.choices(incident_types, weights, k=100)
    incident_counts = Counter(incidents)

    num_reads = incident_counts['r']
    num_updates = incident_counts['u']
    num_inserts = incident_counts['i']

    # select ids for reads, updates, inserts
    read_ids = random.sample(ids, num_reads)
    update_ids = random.sample(ids, num_updates)
    insert_list = [generate_incident() for _ in range(num_inserts)]

    start_time = time.time()
    process = psutil.Process(os.getpid())
    mem_before_exp = process.memory_info().rss / 1024 / 1024  # in MB

    for incident_id in read_ids: 
        query = f"SELECT * FROM logs WHERE ID = '{incident_id}'"
        cursor.execute(query)
        rows = cursor.fetchall()

    for incident_id in update_ids:
        # SQL query to update the incident_state to 'Resolved'
        query= f"""
        UPDATE logs
        SET incident_state = 'Resolved', active = FALSE
        WHERE ID = '{incident_id}'
        """
        cursor.execute(query) 

    for incident in insert_list:
        query = f"""
            INSERT INTO logs (number, incident_state, active, reassignment_count, sys_mod_count, caller_id)
            VALUES ('{incident[0]}', '{incident[1]}', {incident[2]}, '{incident[3]}', '{incident[4]}', '{incident[5]}')
            """
        cursor.execute(query)

    memory_after_exp = process.memory_info().rss / 1024 / 1024  # in MB

    end_time =  time.time()
    
    cursor.close()
    conn.close()

    return end_time - start_time, memory_after_exp - mem_before_exp

def mongo_exp (num_incidents) :
    # Database connection details
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["monte_carlo_db"]  # Database name
    collection = db["logs"]  # Collection name

    # Get a list of all IDs in the collection
    ids = [doc['_id'] for doc in collection.find({}, {'_id': 1})]
    
    # ------------- randomly select incidents ---------------
    # Define the possible incident types and their distribution
    incident_types = ['r', 'u', 'i']
    weights = [0.8, 0.1, 0.1]  # 80% reason, 10% update, 10% insert

    # Generate a list of 100 incidents based on the specified weights
    incidents = random.choices(incident_types, weights, k=100)

    incident_types = ['r', 'u', 'i']
    weights = [0.8, 0.1, 0.1]  # 80% reason, 10% update, 10% insert

    incidents = random.choices(incident_types, weights, k=100)
    incident_counts = Counter(incidents)

    num_reads = incident_counts['r']
    num_updates = incident_counts['u']
    num_inserts = incident_counts['i']

    # select ids for reads, updates, inserts
    read_ids = random.sample(ids, num_reads)
    update_ids = random.sample(ids, num_updates)
    insert_list = [generate_incident() for _ in range(num_inserts)]

    start_time = time.time()
    process = psutil.Process(os.getpid())
    mem_before_exp = process.memory_info().rss / 1024 / 1024  # in MB

    for incident_id in read_ids: 
        incident_data = collection.find_one({'ID': incident_id})

    for incident_id in update_ids:
        # Update the incident data (incident_state to 'Resolved', active to False)
        collection.update_one(
            {'ID': incident_id},  # filter by the incident ID
            {'$set': {'incident_state': 'Resolved', 'active': False}}  # update fields
        )

    incident_documents = [
        {
            'number': incident[0],
            'incident_state': incident[1],
            'active': incident[2],
            'reassignment_count': incident[3],
            'sys_mod_count': incident[4],
            'caller_id': incident[5]
        }
        for incident in insert_list
    ]

    # Insert the generated incident data into MongoDB
    collection.insert_many(incident_documents)

    memory_after_exp = process.memory_info().rss / 1024 / 1024  # in MB

    end_time =  time.time()

    return end_time - start_time, memory_after_exp - mem_before_exp


def simulation(num_experiments, num_daily_incidents):
    # Lists to store results
    mongo_times = []
    mongo_memories = []
    ps_times = []
    ps_memories = []

    # Run experiments and collect results
    for _ in range(num_experiments):
        mongo_tuple = mongo_exp(num_daily_incidents)  
        ps_tuple = postgres_exp(num_daily_incidents)  
        
        mongo_times.append(mongo_tuple[0])
        mongo_memories.append(mongo_tuple[1])
        ps_times.append(ps_tuple[0])
        ps_memories.append(ps_tuple[1])


    # Combined execution time plot
    plt.figure(figsize=(12, 6))

    # Plot MongoDB execution times
    plt.hist(mongo_times, bins=20, color='blue', alpha=0.7, label='MongoDB Execution Time')

    # Plot PostgreSQL execution times
    plt.hist(ps_times, bins=20, color='green', alpha=0.7, label='PostgreSQL Execution Time')

    plt.xlabel('Execution Time (seconds)')
    plt.ylabel('Frequency')
    plt.title('Execution Time Distribution')
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Combined memory usage plot
    plt.figure(figsize=(12, 6))

    # Plot MongoDB memory usage
    plt.hist(mongo_memories, bins=20, color='blue', alpha=0.7, label='MongoDB Memory Usage')

    # Plot PostgreSQL memory usage
    plt.hist(ps_memories, bins=20, color='green', alpha=0.7, label='PostgreSQL Memory Usage')

    plt.xlabel('Memory Usage (MB)')
    plt.ylabel('Frequency')
    plt.title('Memory Usage Distribution')
    plt.legend()

    plt.tight_layout()
    plt.show()

    
simulation(100, 100)










