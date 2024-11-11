from assignment import computeAssingment, BPRcostFunction
from utils import PathUtils, num_of_routes
from dijkstra_routes import read_input, write_results, calculate_routes, unify_same_time_paths, average_paths
from greedy import run_simulation, prep_data
if __name__ == "__main__":
    net_file = str(PathUtils.barcelona_net_file )
    name = net_file.split("/")[-1].split("_")[0]
    # total_system_travel_time_optimal = computeAssingment(net_file=net_file,
    #                                                      algorithm="FW",
    #                                                      costFunction=BPRcostFunction,
    #                                                      systemOptimal=True,
    #                                                      verbose=True,
    #                                                      accuracy=0.00005,
    #                                                      maxIter=6000,
    #                                                      maxTime=6000000,results_file=f'./assignments/{name}_result_SO.txt',force_net_reprocess=True)

    # total_system_travel_time_equilibrium = computeAssingment(net_file=net_file,
    #                                                          algorithm="FW",
    #                                                          costFunction=BPRcostFunction,
    #                                                          systemOptimal=False,
    #                                                          verbose=True,
    #                                                          accuracy=0.00005,
    #                                                          maxIter=6000,
    #                                                          maxTime=6000000, results_file=f'./assignments/{name}_result_UE.txt')

    # print("Computed for: ", name)
    # print("UE - SO = ", total_system_travel_time_equilibrium - total_system_travel_time_optimal)
    
    pairs_SO = []
    read_input(f'./assignments/{name}_result_SO_OD_pairs0001.txt', pairs_SO)
    pairs_SO = calculate_routes(pairs_SO)
    pairs_SO = unify_same_time_paths(pairs_SO)
    write_results(f'./assignments/{name}_result_SO_routes0001.txt', pairs_SO, 'SO')
    
    pairs_UE = []
    read_input(f'./assignments/{name}_result_UE_OD_pairs0001.txt', pairs_UE)
    pairs_UE = calculate_routes(pairs_UE)
    pairs_UE = average_paths(pairs_UE)
    write_results(f'./assignments/{name}_result_UE_routes0001.txt', pairs_UE, 'UE')
    
    # use the greedy algorithm to create assignment
    # for each OD pair in SO run simulation
    
    #TODO: fix near-zero routes in SO - currently ingnored
    
    diff = 0
    len_simul = 200
    for pairSO, pairUE in zip(pairs_SO, pairs_UE):
        if pairSO.origin != pairUE.origin or pairSO.destination != pairUE.destination:
            print("Error: OD pairs do not match")
            break
        if num_of_routes(pairSO.routes) < 2:
            # print("Not enough routes for ", pairSO.origin, pairSO.destination)
            continue
        routes = pairSO.routes
        agents = pairSO.flow
        print("Running simulation for ", pairSO.origin, pairSO.destination)
        agents, routes = prep_data(routes)
        thresholds = [0.01, 0.001, 0.0001]
        results = run_simulation(agents, routes, thresholds,len_simul, 0.0)
        history = results['history']
        mean = results['mean']
        variance = results['variance']
        convergence = results['convergence']
        if not convergence[0]:
            print("Did not converge for ", pairSO.origin, pairSO.destination)
        else:
            print("Converged in ", convergence[1], " steps")
        print("Difference for individual between UE and SO: ", pairUE.routes[0].time - mean[-1]/len_simul)
        diff = diff + pairUE.routes[0].time - mean[-1]/convergence[1]
        print("Mean: ", mean)
        print("Variance: ", variance)
        print("History: ", history)
        print("Agents: ", agents)
        print("Fairness: ", results['fairness'])
        print("Almost convergence: ", results['almost_convergence'])
        print("Fairness standarized: ", results['fairness_stand'])
    
    print("Total difference: ", diff)
    if diff < 0:
        print("UE is better, we lost ")
    else:
        print("Great success, we gained ", diff)