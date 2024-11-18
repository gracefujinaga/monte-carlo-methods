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

    for incident_id in ids:
        # Fetch the incident data based on the random incident ID
        incident_data = collection.find_one({'ID': incident_id})

    client.close()


def update(num_incidents):
    # MongoDB connection
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["monte_carlo_db"]  # Database name
    collection = db["logs"]  # Collection name

    # Get a list of all IDs in the collection
    ids = [doc['_id'] for doc in collection.find({}, {'_id': 1})]

    # Randomly sample the IDs
    ids = random.sample(ids, num_incidents)

    for incident_id in ids:
        # Update the incident data (incident_state to 'Resolved', active to False)
        collection.update_one(
            {'ID': incident_id},  # filter by the incident ID
            {'$set': {'incident_state': 'Resolved', 'active': False}}  # update fields
        )

    client.close()


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

    for incident in incident_list:
        incident_document = {
            'number': incident[0],
            'incident_state': incident[1],
            'active': incident[2],
            'reassignment_count': incident[3],
            'sys_mod_count': incident[4],
            'caller_id': incident[5]
        }
        collection.insert_one(incident_document)

    client.close()

def measure_mongo_query(func, num_incidents) :
    # Measure memory and time usage
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / 1024 / 1024  # in MB
    start_time = time.time()
    
    func(num_incidents)

    end_time = time.time()
    memory_after = process.memory_info().rss / 1024 / 1024  # in MB

    time_taken = end_time - start_time
    memory_used = memory_after-memory_before

    print(f"Mongo {func.__name__} - Time: {time_taken:.4f} seconds, Memory Used: {memory_used} MB")


for count in [10, 100, 1000, 100000]:
    print(f"--------------------{count}-----------------------")
    measure_mongo_query(read, count)
    measure_mongo_query(update, count)
    measure_mongo_query(insert, count)


