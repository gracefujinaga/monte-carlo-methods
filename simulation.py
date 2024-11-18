import psycopg2
import random
import time
import psutil
import os
from pymongo import MongoClient
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

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
    incident_types = ['r', 'u', 'i']
    weights = [0.8, 0.1, 0.1]  # 80% reason, 10% update, 10% insert

    incidents = random.choices(incident_types, weights, k=num_incidents)
    incident_counts = Counter(incidents)

    num_reads = incident_counts['r']
    num_updates = incident_counts['u']
    num_inserts = incident_counts['i']

    # select ids for reads, updates, inserts
    read_ids = random.sample(ids, num_reads)
    update_ids = random.sample(ids, num_updates)
    insert_list = [generate_incident() for _ in range(num_inserts)]

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

    conn.commit()
    cursor.close()
    conn.close()


def mongo_exp (num_incidents) :
    # Database connection details
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["monte_carlo_db"]  # Database name
    collection = db["logs"]  # Collection name

    # Get a list of all IDs in the collection
    ids = [doc['_id'] for doc in collection.find({}, {'_id': 1})]
    
    # ------------- randomly select incidents ---------------
    incident_types = ['r', 'u', 'i']
    weights = [0.8, 0.1, 0.1]  # 80% reason, 10% update, 10% insert

    incidents = random.choices(incident_types, weights, k=num_incidents)
    incident_counts = Counter(incidents)

    num_reads = incident_counts['r']
    num_updates = incident_counts['u']
    num_inserts = incident_counts['i']

    # select ids for reads, updates, inserts
    read_ids = random.sample(ids, num_reads)
    update_ids = random.sample(ids, num_updates)
    insert_list = [generate_incident() for _ in range(num_inserts)]

    for incident_id in read_ids: 
        incident_data = collection.find_one({'_id': incident_id})

    for incident_id in update_ids:
        # Update the incident data (incident_state to 'Resolved', active to False)
        collection.update_one(
            {'_id': incident_id},  # filter by the incident ID
            {'$set': {'incident_state': 'Resolved', 'active': False}}  # update fields
        )

    for incident in insert_list:
        incident_document = {
            'number': incident[0],
            'incident_state': incident[1],
            'active': incident[2],
            'reassignment_count': incident[3],
            'sys_mod_count': incident[4],
            'caller_id': incident[5]
        }
        collection.insert_one(incident_document)

def get_descriptive_stats(data):
    mean = np.mean(data)
    q75, q25 = np.percentile(data, [75 ,25])
    iqr = q75 - q25
    return mean, iqr, np.median(data)

def simulation(num_experiments, num_daily_incidents):
    # Lists to store results
    mongo_times = []
    mongo_memories = []
    ps_times = []
    ps_memories = []

    # Run experiments and collect results
    for _ in range(num_experiments):

        # measure mongo
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # in MB
        start_time = time.time()

        mongo_exp(num_daily_incidents) 

        end_time = time.time()
        memory_after = process.memory_info().rss / 1024 / 1024  # in MB
        mongo_times.append(end_time - start_time)
        mongo_memories.append(memory_after - memory_before)

        # measure postgres
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # in MB
        start_time = time.time()

        postgres_exp(num_daily_incidents) 

        end_time = time.time()
        memory_after = process.memory_info().rss / 1024 / 1024  # in MB
        ps_times.append(end_time - start_time)
        ps_memories.append(memory_after - memory_before)

    # get statistics for mongo
    mongo_mean_time, mongo_iqr_time, mongo_median_time = get_descriptive_stats(mongo_times)
    mongo_mean_mem, mongo_iqr_mem, mongo_median_mem = get_descriptive_stats(mongo_memories)

    # get statistics for postgres
    ps_mean_time, ps_iqr_time, ps_median_time = get_descriptive_stats(ps_times)
    ps_mean_mem, ps_iqr_mem, ps_median_mem = get_descriptive_stats(ps_memories)

    print("MongoDB Execution Time - Mean: {:.4f}, IQR: {:.4f}".format(mongo_mean_time, mongo_iqr_time, mongo_median_time))
    print("PostgreSQL Execution Time - Mean: {:.4f}, IQR: {:.4f}".format(ps_mean_time, ps_iqr_time, ps_median_time))
    print("MongoDB Memory Usage - Mean: {:.4f}, IQR: {:.4f}".format(mongo_mean_mem, mongo_iqr_mem, mongo_median_mem))
    print("PostgreSQL Memory Usage - Mean: {:.4f}, IQR: {:.4f}".format(ps_mean_mem, ps_iqr_mem, ps_median_mem))

    # Create a figure with 4 subplots (2 rows, 2 columns)
    fig, axs = plt.subplots(2, 2, figsize=(8, 8))

    # MongoDB Memory Histogram
    axs[0, 0].hist(mongo_memories, bins='auto', color='blue', alpha=0.7)
    axs[0, 0].set_title(f'MongoDB Memory Usage')
    axs[0, 0].set_xlabel('Memory Usage (MB)')
    axs[0, 0].set_ylabel('Frequency')

    # PostgreSQL Memory Histogram
    axs[0, 1].hist(ps_memories, bins='auto', color='green', alpha=0.7)
    axs[0, 1].set_title(f'PostgreSQL Memory Usage')
    axs[0, 1].set_xlabel('Memory Usage (MB)')
    axs[0, 1].set_ylabel('Frequency')

    # MongoDB Execution Time Histogram
    axs[1, 0].hist(mongo_times, bins='auto', color='blue', alpha=0.7)
    axs[1, 0].set_title(f'MongoDB Execution Time')
    axs[1, 0].set_xlabel('Execution Time (seconds)')
    axs[1, 0].set_ylabel('Frequency')

    # PostgreSQL Execution Time Histogram
    axs[1, 1].hist(ps_times, bins='auto', color='green', alpha=0.7)
    axs[1, 1].set_title(f'PostgreSQL Execution Time')
    axs[1, 1].set_xlabel('Execution Time (seconds)')
    axs[1, 1].set_ylabel('Frequency')

    plt.tight_layout()
    plt.show()

simulation(100, 100)










