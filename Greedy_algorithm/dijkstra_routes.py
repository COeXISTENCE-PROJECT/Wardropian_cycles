import networkx as nx
import numpy as np
from os import listdir
from os.path import isfile, join
from utils import round_trip_time_and_flow, PATH, _debug, ROUND
# in this file I create routes from times and flows on each segment using Dijkstra algorithm for finding shortest path in the graph.


class Route:
    def __init__(self, time: float, flow: float, path: list):
        self.time = time
        self.flow = flow
        self.path = path

class OD_pair:
    def __init__(self, origin: str, destination: str, flow: float):
        self.origin = origin
        self.destination = destination
        self.flow = flow
        self.graph = {}
        self.routes = []
        
    def add_graph(self, graph: nx.Graph):
        self.graph = graph
    
    def add_routes(self, routes: Route):
        self.routes.append(routes)

def read_input(filename: str, pairs: list):
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
            graph = nx.Graph()
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
    
            

def write_results(filename: str, pairs: list):    
    with open(filename, 'w') as f:
        f.write("origin destination total_flow\n")
        f.write("time flow path\n")
        for pair in pairs:
            f.write(f'{pair.origin} {pair.destination} {pair.flow}\n')
            for route in pair.routes:
                f.write(f'{route.time} {route.flow} ')
                for node in route.path:
                    f.write(f'{node} ')
                f.write('\n')        
    

def calculate_routes(pairs: list):
    for pair in pairs:
        graph = pair.graph
        routes = {}
        o = pair.origin
        d = pair.destination
        
        if _debug:
            print(o, d)
            print(graph.edges(data=True))
        
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
                od_route = Route(sum_time, min_flow, route)
                  
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
        

if __name__ == "__main__":
    
    # list all files from the directory PATH
    files = listdir(PATH)    
    # filter only files with SO in the name
    files = [f for f in files if 'SO_OD_pairs' in f and isfile(join(PATH, f))]
    for f in files:
        pairs = []
        read_input(PATH + f, pairs)
        calculate_routes(pairs)
        write_results(f.replace('OD_pairs', 'paths'), pairs)
    pass