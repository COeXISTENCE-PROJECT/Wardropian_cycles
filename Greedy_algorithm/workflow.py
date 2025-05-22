from assignment import computeAssignment, BPRcostFunction
from utils import PathUtils, num_of_routes
from dijkstra_routes import read_input, write_results, calculate_routes, unify_same_time_paths, average_paths
from greedy import run_simulation, prep_data

_compute_assignments = False
_compute_CSO = False

if __name__ == "__main__":
    net_file = str(PathUtils.barcelona_net_file)
    name = net_file.split("/")[-1].split("_")[0]
    if _compute_assignments:
        total_system_travel_time_optimal = computeAssignment(net_file=net_file,
                                                            algorithm="FW",
                                                            costFunction=BPRcostFunction,
                                                            systemOptimal=True,
                                                            verbose=True,
                                                            accuracy=0.000005,
                                                            maxIter=6000,
                                                            maxTime=6000000,results_file=f'./assignments/{name}_result_SO.txt',force_net_reprocess=True)

        total_system_travel_time_equilibrium = computeAssignment(net_file=net_file,
                                                                algorithm="FW",
                                                                costFunction=BPRcostFunction,
                                                                systemOptimal=False,
                                                                verbose=True,
                                                                accuracy=0.000005,
                                                                maxIter=6000,
                                                                maxTime=6000000, results_file=f'./assignments/{name}_result_UE.txt')

        if _compute_CSO:
            total_system_travel_time_constrained_optimal = computeAssignment(net_file=net_file,
                                                                algorithm="FW",
                                                                costFunction=BPRcostFunction,
                                                                systemOptimal=True,
                                                                verbose=True,
                                                                accuracy=0.00005,
                                                                maxIter=6000,
                                                                maxTime=6000000, results_file=f'./assignments/{name}_result_CSO.txt',
                                                                CSO=(True,f'./assignments/{name}_result_UE.txt'))

        print("Computed for: ", name)
        # print("UE - SO = ", total_system_travel_time_equilibrium - total_system_travel_time_optimal)
        # if _compute_CSO:
        #     print("CSO - SO = ", total_system_travel_time_constrained_optimal - total_system_travel_time_optimal)
    
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
    
    if _compute_CSO:
        pairs_CSO = []
        read_input(f'./assignments/{name}_result_SO_CSO_OD_pairs.txt', pairs_CSO)
        pairs_CSO = calculate_routes(pairs_CSO)
        pairs_CSO = unify_same_time_paths(pairs_CSO)
        write_results(f'./assignments/{name}_result_CSO_routes.txt', pairs_CSO, 'CSO')
    
    
    # use the greedy algorithm to create assignment
    # for each OD pair in SO run simulation
    
    diff = 0
    len_simul = 200
    for pairSO, pairUE, in zip(pairs_SO, pairs_UE):
        if pairSO.destination != 101:
            continue
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
        thresholds = [0.33, 0.2, 0.1]
        print("Agents: ", agents)
        print("Routes: ", routes)
        results = run_simulation(agents, routes, thresholds,len_simul, 0.0)
        history = results['history']
        mean = results['mean']
        variance = results['variance']
        convergence = results['convergence']
        if not convergence[0]:
            print("Did not converge for ", pairSO.origin, pairSO.destination)
        else:
            print("Converged in ", convergence[1], " steps")
        print("Difference for individual between UE and SO: ", pairUE.routes[0].time - mean[-1]/len_simul, pairUE.routes[0].time)
        diff = diff + pairUE.routes[0].time - mean[-1]/len_simul
        # print("Mean: ", mean)
        # print("Variance: ", variance)
        # print("History: ", history)
        # print("Agents: ", agents)
        # print("Fairness: ", results['fairness'])
        # print("Almost convergence: ", results['almost_convergence'])
        # print("Fairness normalized: ", results['fairness_norm'])
        break
    print("Total difference: ", diff)
    if diff < 0:
        print("UE is better, we lost ")
    else:
        print("Great success, we gained ", diff)
    