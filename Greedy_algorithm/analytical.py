from utils import *
from dijkstra_routes import read_input, calculate_routes, unify_same_time_paths
from math import gcd

def solve_pair(OD_pair):
    result = {}
    agents = sum([round(route.flow) for route in OD_pair.routes])
    result["naive"] = agents
    # try to find the greatest common divisor
    pair_gcd = gcd(*[round(route.flow) for route in OD_pair.routes])
    if(pair_gcd > 1):
        agents = agents // pair_gcd
    result["gcd"] = agents
    return result

def analytical_simulation(pairs):
    res = []
    for pair in pairs:
        if num_of_routes(pair.routes) < 2:
            res.append({"origin": pair.origin, "destination": pair.destination, "naive": 0, "gcd": 0})
            continue
        res.append({"origin": pair.origin, "destination": pair.destination, **solve_pair(pair)})
    return res
        

# Example usage of the analytical_simulation function    
if __name__ == "__main__":
    
    name = str(PathUtils.barcelona_net_file )
    name = name.split("/")[-1].split("_")[0]
    pairs_SO = []
    read_input(f'./assignments/{name}_result_SO_OD_pairs0001.txt', pairs_SO)
    pairs_SO = calculate_routes(pairs_SO)
    pairs_SO = unify_same_time_paths(pairs_SO)
    
    res = analytical_simulation(pairs_SO)
    
    # Output the results
    for r in res:
        if r["naive"] == 0:
            continue
        print("OD pair:", r["origin"],"-", r["destination"], sep="")
        print("Naive cycle length (# of agents): ", r["naive"])
        print("GCD cycle length: ", r["gcd"])
        