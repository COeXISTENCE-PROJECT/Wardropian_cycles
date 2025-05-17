from utils import *
from dijkstra_routes import read_input, calculate_routes, unify_same_time_paths
from math import gcd
from random import randint
from utils import Route, OD_pair

def solve_pair(OD_pair):
    '''
    Solve the OD pair using the analytical solution.
    
    Parameters:
        OD_pair (OD_pair): The OD pair to solve. The OD pair should have a list of routes.
        
    Returns:
        dict: A dictionary containing the number of agents needed for the naive and gcd solutions.
    '''
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
    '''
    Analytically solve the OD pairs.
    
    Parameters:
        pairs (list of OD_pair): The OD pairs to solve.
        
    Returns:
        list: A list of dictionaries containing the lengths of cycles in the naive and gcd solutions.
    '''
    res = []
    for pair in pairs:
        if num_of_routes(pair.routes) < 2:
            res.append({"origin": pair.origin, "destination": pair.destination, "naive": 0, "gcd": 0})
            continue
        res.append({"origin": pair.origin, "destination": pair.destination, **solve_pair(pair)})
    return res
        

# Example usage of the analytical_simulation function    
if __name__ == "__main__":
    
    # pairs_SO = []
    # for i in range(1,10):
    #     pair = OD_pair(i, i+1, 0.0)
    #     for j in range(1,randint(2,5)):
    #         time = randint(1,10)
    #         flow = randint(1,10)
    #         pair.add_routes(Route(time, flow, j))
    #     pair.recalculate_flow()
    #     pairs_SO.append(pair)
    net_file = str(PathUtils.sioux_falls_net_file)
    name = net_file.split("/")[-1].split("_")[0]
    
    pairs_CSO = []
    read_input(f'./assignments/{name}_result_SO_OD_pairs.txt', pairs_CSO)
    pairs_CSO = calculate_routes(pairs_CSO)
    pairs_CSO = unify_same_time_paths(pairs_CSO)
    # write_results(f'./assignments/{name}_result_CSO_routes.txt', pairs_CSO, 'CSO')

        
    res = analytical_simulation(pairs_CSO)
    
    # Output the results
    for r in res:
        if r["naive"] == 0:
            continue
        print("OD pair: ", r["origin"],"-", r["destination"], sep="")
        print("Naive cycle length (# of agents): ", r["naive"])
        print("GCD cycle length: ", r["gcd"])
        