# from UE_routes file make a csv file with the following columns:
#     - origin
#     - destination
#     - time
#     - flow

# this file might have multiple routes with the same origin and destination
# we need to take time of the first route and sum the flow of all routes with the same origin and destination

import pandas as pd
import numpy as np
import networkx as nx

class CSVRecord:
    def __init__(self, origin, destination, link_origin, link_destination, time, flow):
        self.origin = origin
        self.destination = destination
        self.link_origin = link_origin  
        self.link_destination = link_destination
        self.time = time
        self.flow = flow        

    
if __name__ == "__main__":
    # read from the file of the format:
    #   OD PAIRS
    #  origin	destination	demand
    #  link_origin	link_destination	flow	time
    #  ...
    #  into a list of CSVRecord objects
    records = []
    f = "./assignments/SiouxFalls_result_UE_OD_pairs.txt"
    
    with open(f, 'r') as file:
        lines = file.readlines()
        lines = lines[3:]
        i = 0
        while i < len(lines):
            origin, destination, demand = lines[i].split()
            demand = float(demand)
            for j in range(i+1, len(lines)):
                edge = lines[j]
                if edge == '\n':
                    i = j + 1
                    break
                print(edge)
                link_origin, link_destination, flow, time = edge.split()
                flow = float(flow)
                time = float(time)
                records.append(CSVRecord(origin, destination, link_origin, link_destination, time, flow))
                
    # create a DataFrame from the records
    df = pd.DataFrame([record.__dict__ for record in records])
    print(df.head())
    df.to_csv("SiouxFalls_result_UE_OD_pairs.csv", index=False)