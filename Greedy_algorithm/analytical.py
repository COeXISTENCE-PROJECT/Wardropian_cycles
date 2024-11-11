from utils import *
from dijkstra_routes import read_input, calculate_routes, unify_same_time_paths
from math import gcd
if __name__ == "__main__":
    
    name = str(PathUtils.eastern_massachusetts_net_file )
    name = name.split("/")[-1].split("_")[0]
    pairs_SO = []
    read_input(f'./assignments/{name}_result_SO_OD_pairs.txt', pairs_SO)
    pairs_SO = calculate_routes(pairs_SO)
    pairs_SO = unify_same_time_paths(pairs_SO)
    # calculate the lenght of the cycles in a simple way and try to shorten them using GCD
    
    for pair in pairs_SO:
        if num_of_routes(pair.routes) < 2:
            continue
        print("OD pair: ",pair.origin,"-",pair.destination, sep="")
        agents = sum([round(route.flow) for route in pair.routes])
        print("Naive cycle length (# of agents): ", agents)
        # try to find the greatest common divisor
        pair_gcd = gcd(*[round(route.flow) for route in pair.routes])
        if(pair_gcd > 1):
            agents = agents // pair_gcd
        print("GCD cycle length: ", agents)
        