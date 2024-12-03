import networkx as nx
import numpy as np
from os import listdir
from os.path import isfile, join
from utils import round_trip_time_and_flow, PATH, _debug, ROUND, OD_pair, Route
# in this file I create routes from times and flows on each segment using Dijkstra algorithm for finding shortest path in the graph.



def read_input(filename: str, pairs: list):
    '''
    Read the input file and create OD pairs using the graph representing the network
    
    Parameters:
        filename: str - the name of the file to read
        pairs: list - the list of OD pairs to be filled
    
    Returns:
        None
    '''
    with open(filename, 'r') as f:
        lines = f.readlines()
        # skip the header
        lines = lines[3:]
        # read the pairs
        i = 0
        while i < len(lines):
            origin, destination, flow = lines[i].split()
            flow = float(flow)
            pair = OD_pair(origin, destination, flow)
            # read the graph
            graph = nx.DiGraph()
            for j in range(i+1, len(lines)):
                edge = lines[j]
                if edge == '\n':
                    i = j + 1
                    break
                origin, destination, flow, time = round_trip_time_and_flow(edge, ROUND)
                graph.add_edge(origin, destination, flow=flow, time=time)
            pair.add_graph(graph)
            if pair.flow > 0:
                # we consider only pairs with flow > 0
                pairs.append(pair)

        
    if _debug:
        for pair in pairs:
            print(pair.origin, pair.destination, pair.flow)
            print(pair.graph.edges(data=True))
            print()

def unify_same_time_paths(pairs: list):
    '''
    Unify paths with the same time, changes are made in place
    
    Parameters:
        pairs: list - the list of OD pairs
        
    Returns:
        None
    '''
    for pair in pairs:
        if len(pair.routes) == 1:
            continue
        for i in range(len(pair.routes)):
            for j in range(i+1, len(pair.routes)):
                if abs(pair.routes[i].time - pair.routes[j].time) < 1e-9:
                    pair.routes[i].flow += pair.routes[j].flow
                    pair.routes[j].flow = 0
        pair.routes = [route for route in pair.routes if route.flow > 0]
    return pairs

def average_paths(pairs: list):
    '''
    Make average path out of paths with the same origin and destination - used for UE (since this is the UE assumption)
    Changes are made in place
    
    Parameters:
        pairs: list - the list of OD pairs
        
    Returns:
        None
    '''
    for pair in pairs:
        if len(pair.routes) == 1:
            continue
        avg_time = 0
        flow = 0
        for route in pair.routes:
            avg_time += route.time * route.flow
            flow += route.flow
        avg_time /= flow
        for route in pair.routes:
            route.time = avg_time
    return pairs
            

def write_results(filename: str, pairs: list, asignment_type = 'SO'):    
    with open(filename, 'w') as f:
        f.write("origin destination total_flow\n")
        f.write("time flow nodes_in_path\n")
        for pair in pairs:
            # ignore pairs with only one route
            if asignment_type == 'SO':
                if len(pair.routes) == 1:
                    continue
            f.write(f'{pair.origin} {pair.destination} {pair.flow}\n')
            for route in pair.routes:
                f.write(f'{route.time} {route.flow} ')
                for node in route.path:
                    f.write(f'{node} ')
                f.write('\n')        
            f.write('\n')
    

def calculate_routes(pairs: list):
    '''
    Calculate the routes for each OD pair using Dijkstra algorithm from the graph
    
    Parameters:
        pairs: list - the list of OD pairs
        
    Returns:
        list - the list of OD pairs with routes filled and flows updated
    '''
    for pair in pairs:
        graph = pair.graph
        routes = {}
        o = pair.origin
        d = pair.destination
        
        if _debug:
            print(o, d)
            print(graph.edges(data=True))
            #plot graph
            import matplotlib.pyplot as plt
            pos = nx.spring_layout(graph)
            nx.draw(graph, pos, with_labels=True)
            labels = nx.get_edge_attributes(graph, 'time')
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
            plt.show()
        
        while True:
            try:
                route = nx.dijkstra_path(graph, o, d, weight='time')
                routes[(o, d)] = route
                # find the minimum flow on the route
                min_flow = np.inf
                for i in range(len(route) - 1):
                    if graph[route[i]][route[i+1]]['flow'] < min_flow:
                        min_flow = graph[route[i]][route[i+1]]['flow']
                # update the flow on the route
                for i in range(len(route) - 1):
                    graph[route[i]][route[i+1]]['flow'] -= min_flow
                
                sum_time = 0
                for i in range(len(route) - 1):
                    sum_time += graph[route[i]][route[i+1]]['time']
                od_route = Route(sum_time, min_flow, pair.get_num_routes(), route)
                  
                # remove the empty edges
                for i in range(len(route) - 1):
                    if graph[route[i]][route[i+1]]['flow'] == 0:
                        graph.remove_edge(route[i], route[i+1])
                
                pair.add_routes(od_route)
                if _debug:
                    print("route:", route)
                    print(min_flow)
                    print(sum_time)
                    print()
            except nx.NetworkXNoPath:
                break
    return pairs
        

if __name__ == "__main__":
    
    # list all files from the directory PATH
    files = listdir(PATH)    
    # filter only files with SO in the name
    files = [f for f in files if 'SO_OD_pairs' in f and isfile(join(PATH, f))]
    for f in files:
        pairs = []
        read_input(PATH + f, pairs)
        calculate_routes(pairs)
        pairs = unify_same_time_paths(pairs)
        write_results(f.replace('OD_pairs', 'paths'), pairs)
    pass