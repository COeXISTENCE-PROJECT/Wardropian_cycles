from assignment import computeAssingment, BPRcostFunction
from utils import PathUtils
from dijkstra_routes import read_input, write_results, calculate_routes, unify_same_time_paths, average_paths
from greedy import run_simulation, prep_data
if __name__ == "__main__":
    net_file = str(PathUtils.sioux_falls_net_file )
    name = net_file.split("/")[-1].split("_")[0]
    # total_system_travel_time_optimal = computeAssingment(net_file=net_file,
    #                                                      algorithm="FW",
    #                                                      costFunction=BPRcostFunction,
    #                                                      systemOptimal=True,
    #                                                      verbose=True,
    #                                                      accuracy=0.00001,
    #                                                      maxIter=25000,
    #                                                      maxTime=6000000,results_file=f'./assignments/{name}_result_SO.txt',force_net_reprocess=True)

    # total_system_travel_time_equilibrium = computeAssingment(net_file=net_file,
    #                                                          algorithm="FW",
    #                                                          costFunction=BPRcostFunction,
    #                                                          systemOptimal=False,
    #                                                          verbose=True,
    #                                                          accuracy=0.00001,
    #                                                          maxIter=6000,
    #                                                          maxTime=6000000, results_file=f'./assignments/{name}_result_UE.txt')

    # print("Computed for: ", name)
    # print("UE - SO = ", total_system_travel_time_equilibrium - total_system_travel_time_optimal)
    
    pairs_SO = []
    read_input(f'./assignments/{name}_result_SO_OD_pairs.txt', pairs_SO)
    pairs_SO = calculate_routes(pairs_SO)
    pairs_SO = unify_same_time_paths(pairs_SO)
    write_results(f'./assignments/{name}_result_SO_routes.txt', pairs_SO, 'SO')
    
    pairs_UE = []
    read_input(f'./assignments/{name}_result_UE_OD_pairs.txt', pairs_UE)
    pairs_UE = calculate_routes(pairs_UE)
    pairs_UE = average_paths(pairs_UE)
    write_results(f'./assignments/{name}_result_UE_routes.txt', pairs_UE, 'UE')
    
    # use the greedy algorithm to create assignment
    # for each OD pair in SO run simulation
    
    #TODO: fix near-zero routes in SO
    
    #TODO: something breaks for 22:17 OD pair
    
    for pairSO, pairUE in zip(pairs_SO, pairs_UE):
        if pairSO.origin != pairUE.origin or pairSO.destination != pairUE.destination:
            print("Error: OD pairs do not match")
            break
        if len(pairSO.routes) < 2:
            continue
        routes = pairSO.routes
        agents = pairSO.flow
        print("Running simulation for ", pairSO.origin, pairSO.destination)
        agents, routes = prep_data(routes)
        results = run_simulation(agents, routes, 100, 0.0001)
        history = results['history']
        mean = results['mean']
        variance = results['variance']
        convergence = results['convergence']
        print("Converged: ", convergence)
        print("Mean: ", mean)
        print("Variance: ", variance)
        print("History: ", history)    