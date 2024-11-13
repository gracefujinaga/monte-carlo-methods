# monte-carlo-methods
MSDS 460 Assignment 4

# Data source
https://www.kaggle.com/datasets/vipulshinde/incident-response-log?resource=download

# Experiments conducted

The first benchmark experiment compared mongodb and postgres over reads, inserts, and updates of different sizes: 10, 100, 1000. The outputs of this experiment are in outputs.txt and show the measured memory and time it took to conduct the experiments

The second experiment simulates a specified number of days in the company with incident logs. A simulation of 100 incident log database interactions were conducted 100 times. For each 100 incident log interactions, around 80% were read, 10% insert, 10% update. The number was randomly selected for each 100 times with those as the weights. Then, the memory, time components were measured and aggregated over the 100 simulations. The id of the records inserted/updated/read were randomly selected with replacement. 

# Todo items
The outputs for the graphs are incomplete don't look right. The memory usage is sometimes negative... this doesn't really make sense, especially for read operations. 
