from collections import deque
from utils import *
from dijkstra_routes import read_input, calculate_routes, unify_same_time_paths
from math import gcd
from random import randint
from utils import Route, OD_pair, Agent
from matplotlib import pyplot as plt
import scienceplots

plt.style.use(['science', 'grid', 'no-latex'])

def optimal_cycle_order(routes):
    '''
    Calculate the optimal cycle order for the routes.
    
    Parameters:
        routes (list of Route): The routes to calculate the cycle order for.
        
    Returns:
        list: A list of route indices in order optimiing the cycle fairness.
    '''
    unit_routes = []
    for i, route in enumerate(routes):
        if route.flow > 0:
            unit_routes.extend([(route, i)] * round(route.flow))
        
    unit_routes.sort(key=lambda x: x[0].time)
    delta = max([route[0].time for route in unit_routes]) - min([route[0].time for route in unit_routes])
    avg_time = np.sum([route[0].time for route in unit_routes]) / len(unit_routes)
    unit_routes = [(route[0].time - avg_time, route[1]) for route in unit_routes] #  sum of time is 0
    delta_pos = max([route[0] for route in unit_routes])
    delta_neg = min([route[0] for route in unit_routes])
    # print("deltas: ", delta,  delta_pos, delta_neg)
    
    route_queue = deque(unit_routes)
    cycle_order = []
    sums = [0]
    sum = 0
    while route_queue:
        if sum > 0: # we take from the left - negative times
            route = route_queue.popleft()
        else: # we take from the right - positive times 
            route = route_queue.pop()
        cycle_order.append(route[1])
        sum += route[0]
        sums.append(sum)
    return cycle_order, avg_time

def random_cycle_order(routes):
    '''
    Calculate the cycle order for the routes in a naive way.
    
    Parameters:
        routes (list of Route): The routes to calculate the cycle order for.
        
    Returns:
        list: A list of route indices in order.
    '''
    cycle_order = []
    for i, route in enumerate(routes):
        if route.flow > 0:
            cycle_order.extend([i] * round(route.flow))
    avg_time = np.sum([routes[route].time for route in cycle_order]) / len(cycle_order)
    sums = [0]
    sum = 0
    np.random.shuffle(cycle_order)  # Shuffle the cycle order randomly
    for route in np.random.permutation(cycle_order):
        sums.append(sum)
        sum += routes[route].time
    return cycle_order, avg_time

def stupid_cycle_order(routes):
    '''
    Calculate the cycle order for the routes in a naive way.
    
    Parameters:
        routes (list of Route): The routes to calculate the cycle order for.
        
    Returns:
        list: A list of route indices in order.
    '''
    cycle_order = []
    for i, route in enumerate(routes):
        if route.flow > 0:
            cycle_order.extend([i] * round(route.flow))
    avg_time = np.sum([routes[route].time for route in cycle_order]) / len(cycle_order)
    sums = [0]
    sum = 0
    for route in cycle_order:
        sums.append(sum)
        sum += routes[route].time
    return cycle_order, avg_time


def find_inequity_of_cycle(routes,cycle_order, avg_time):
    Q = len(cycle_order)
    deviations = np.zeros(Q) 
    inequities = np.zeros((Q, Q)) # inequities[i][j] = inequity of agent j on day i
    route_choice = [[] for _ in range(Q)] # route_choice[i][j] = route chosen by agent j on day i
    for i in range(Q): # days
        for j in range(Q): # agents
            deviations[j] += routes[cycle_order[(i+j) % Q]].time - avg_time
            route_choice[j].append(cycle_order[(i+j) % Q]) # route chosen by agent j on day i
            inequities[i][j] = deviations[j]**2
    
    # calculate the inequity for each day - average for each agent
    # print("final deviations: ", deviations)
    inequity = [np.mean(inequities[i]) for i in range(Q)]
    # print("route choices: ", route_choice[0])
    # print(len(route_choice[0]), len(route_choice))
    return inequity

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
        opt_cycle, avg_time = optimal_cycle_order(pair.routes)
        inequity = find_inequity_of_cycle(pair.routes, opt_cycle, avg_time)
        res.append({"origin": pair.origin, "destination": pair.destination, **solve_pair(pair), "inequity": inequity})
    return res

def cycle_test():
    # raw_route_data = [(14, 55.0), (3, 57.0), (4, 56)]
    raw_route_data = [(4,15), (6,14), (8,9)]
    max_ineq = 9 # max diff squared
    routes = [Route(t, q, j) for j, (q, t) in enumerate(raw_route_data)]
    print("Routes: ", routes)
    opt_cycle,avg_time_opt= optimal_cycle_order(routes)
    print("Optimal cycle order: ", opt_cycle)
    random_inequalities = []
    for i in range(10):
        rand_cycle, avg_time_rand = random_cycle_order(routes)
        random_inequalities.append(find_inequity_of_cycle(routes, rand_cycle, avg_time_rand))
        print(len(random_inequalities[-1]))
    rand_cycle,avg_time_rand= random_cycle_order(routes)
    # print("Random cycle order: ", rand_cycle)
    stupid_cycle,avg_time_stupid= stupid_cycle_order(routes)
    # print("Stupid cycle order: ", stupid_cycle)
    inequity_opt = find_inequity_of_cycle(routes, opt_cycle, avg_time_opt)
    print("Inequity of optimal cycle: ", inequity_opt, len(inequity_opt))
    inequity_random_avg = np.mean(random_inequalities, axis=0)
    print("Inequity of average random cycle: ", inequity_random_avg, len(inequity_random_avg))
    inequity_stupid = find_inequity_of_cycle(routes, stupid_cycle, avg_time_stupid)
    print("Inequity of stupid cycle: ", inequity_stupid, len(inequity_stupid))
    # plot all inequities together
    # add 0 at the beginning of each inequity list to align them
    inequity_opt = [0] + inequity_opt
    inequity_stupid = [0] + inequity_stupid
    inequity_random_avg = [0] + list(inequity_random_avg)
    plt.plot(inequity_opt, label='Optimal Cycle')
    plt.plot(inequity_stupid, label='Stupid Cycle')
    plt.plot(inequity_random_avg, label='Average Random Cycle')
    plt.axhline(y=0, color='r', linestyle='--', label='Zero Inequity')
    plt.axhline(y=max_ineq, color='g', linestyle='--', label='Inequity bound from Proposition 3')
    plt.xlabel('Days')
    plt.ylabel('Inequity')
    plt.title('Inequity over Time for Different Cycle Orders')
    plt.xticks(range(0,len(inequity_opt),2))
    # move legend outside the plot
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.savefig('inequity_cycle_test.png')
    plt.show()
    

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

    net_file = str(PathUtils.barcelona_net_file)
    name = net_file.split("/")[-1].split("_")[0]
    
    OD_pairs = []
    read_input(f'./assignments/{name}_result_SO_OD_pairs.txt', OD_pairs)
    OD_pairs = calculate_routes(OD_pairs)
    OD_pairs = unify_same_time_paths(OD_pairs)
    # write_results(f'./assignments/{name}_result_CSO_routes.txt', OD_pairs, 'CSO')

        
    res = analytical_simulation(OD_pairs)
    
    df = pd.DataFrame(res)
    df.to_csv(f'./assignments/{name}_analytical_results.csv', index=False)
    # Output the results
    for r in res:
        if r["naive"] == 0:
            continue
        print("OD pair: ", r["origin"],"-", r["destination"], sep="")
        print("Naive cycle length (# of agents): ", r["naive"])
        print("GCD cycle length: ", r["gcd"])
        print("Inequity: ", r["inequity"])
        inequity_first_day = r["inequity"][0]
        print("Normalized Inequity: ", [x/ inequity_first_day for x in r["inequity"]])
        