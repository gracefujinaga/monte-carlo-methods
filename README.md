# monte-carlo-methods
MSDS 460 Assignment 4

Grace Fujinaga, Timmy Li, Kevin Ou, John Leigh

# Data source
https://www.kaggle.com/datasets/vipulshinde/incident-response-log?resource=download

# Overview of Contents

The accompanying paper is in the Analysis.pdf file

database_setup.ipynb describes how to set up the experiments and the databases.

The first benchmark study code is in mongo_experiments.py and ps_experiments.py. 

The simulation benchmark study is in simulation.py.

The results are in /Outputs folder. The output.txt has the command line outputs from all three files and the
results.png file has the visualizations fromt he simulation.py file.

All of the data and relevant data dictionary are in the Data folder

# Abstract
In order to compare PostgreSQL and MongoDB, a benchmark study was created. A real set of data was used. The data is an event log of an incident management process gathered from an audit system of an instance of the ServiceNowTM platform with about 120,000 tickets. Logging tickets and fixes for software projects is commonplace, and addressing these tickets is essential in creating and maintaining an efficient, useful software product. The hypothetical question here is which database a company should use to handle their incident tickets. 

# Experiments conducted
The first benchmark experiment compared mongodb and postgres over reads, inserts, and updates of different sizes: 10, 100, 1000. The outputs of this experiment are in outputs.txt and show the measured memory and time it took to conduct the experiments

The second experiment simulates a specified number of days in the company with incident logs. A simulation of 100 incident log database interactions were conducted 100 times. For each 100 incident log interactions, around 80% were read, 10% insert, 10% update. The number was randomly selected for each 100 times with those as the weights. Then, the memory, time components were measured and aggregated over the 100 simulations. The id of the records inserted/updated/read were randomly selected with replacement. 

