import random
from pymongo import MongoClient
import pymongo
import random
import psutil
import os
import time


# Function to fetch incident data from MongoDB
def read(num_incidents):
    # MongoDB connection details
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["monte_carlo_db"]  # Database name
    collection = db["logs"]  # Collection name

    # Get a list of all IDs in the collection
    ids = [doc['_id'] for doc in collection.find({}, {'_id': 1})]

    # Randomly sample the IDs
    ids = random.sample(ids, num_incidents)

    # Track memory usage before and after fetching
    process = psutil.Process(os.getpid())
    memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB

    for incident_id in ids:
        # Fetch the incident data based on the random incident ID
        incident_data = collection.find_one({'ID': incident_id})

    memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB

    client.close()
    
    return memory_after_fetch - memory_before_query

def update(num_incidents):
    # MongoDB connection
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["monte_carlo_db"]  # Database name
    collection = db["logs"]  # Collection name

    # Get a list of all IDs in the collection
    ids = [doc['_id'] for doc in collection.find({}, {'_id': 1})]

    # Randomly sample the IDs
    ids = random.sample(ids, num_incidents)

    # Track memory usage before and after the update
    process = psutil.Process(os.getpid())
    memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB

    for incident_id in ids:
        # Update the incident data (incident_state to 'Resolved', active to False)
        collection.update_one(
            {'ID': incident_id},  # filter by the incident ID
            {'$set': {'incident_state': 'Resolved', 'active': False}}  # update fields
        )

    memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB

    client.close()

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
    # MongoDB connection
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['monte_carlo_db']
    collection = db['logs']

    # Generate a list of incident data
    incident_list = [generate_incident() for _ in range(num_incidents)]

    # Prepare incident data for insertion
    incident_documents = [
        {
            'number': incident[0],
            'incident_state': incident[1],
            'active': incident[2],
            'reassignment_count': incident[3],
            'sys_mod_count': incident[4],
            'caller_id': incident[5]
        }
        for incident in incident_list
    ]

    # Track memory usage before insertion
    process = psutil.Process(os.getpid())
    memory_before_query = process.memory_info().rss / 1024 / 1024  # in MB

    # Insert the generated incident data into MongoDB
    collection.insert_many(incident_documents)

    # Measure memory usage after insertion
    memory_after_fetch = process.memory_info().rss / 1024 / 1024  # in MB

    client.close()

    return memory_after_fetch - memory_before_query

def measure_mongo_query(func, num_incidents) :
    # Measure memory and time usage
    #process = psutil.Process(os.getpid())
    # memory_before = process.memory_info().rss / 1024 / 1024  # in MB
    start_time = time.time()

    mem_usage = func(num_incidents)

    end_time = time.time()
    # memory_after = process.memory_info().rss / 1024 / 1024  # in MB

    time_taken = end_time - start_time
    memory_used = mem_usage

    print(f"Mongo {func.__name__} - Time: {time_taken:.4f} seconds, Memory Used: {memory_used} MB")


for count in [10, 100, 1000]:
    print(f"--------------------{count}-----------------------")
    measure_mongo_query(read, count)
    measure_mongo_query(update, count)
    measure_mongo_query(insert, count)


