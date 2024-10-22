from assignment import computeAssingment, BPRcostFunction
from utils import PathUtils
from dijkstra_routes import read_input, write_results, calculate_routes
if __name__ == "__main__":
    net_file = str(PathUtils.eastern_massachusetts_net_file )
    name = net_file.split("/")[-1].split("_")[0]
    total_system_travel_time_optimal = computeAssingment(net_file=net_file,
                                                         algorithm="FW",
                                                         costFunction=BPRcostFunction,
                                                         systemOptimal=True,
                                                         verbose=True,
                                                         accuracy=0.00005,
                                                         maxIter=2000,
                                                         maxTime=6000000,results_file=f'./assignments/{name}_result_SO.txt',force_net_reprocess=True)

    total_system_travel_time_equilibrium = computeAssingment(net_file=net_file,
                                                             algorithm="FW",
                                                             costFunction=BPRcostFunction,
                                                             systemOptimal=False,
                                                             verbose=True,
                                                             accuracy=0.00001,
                                                             maxIter=10000,
                                                             maxTime=6000000, results_file=f'./assignments/{name}_result_UE.txt')

    print("Computed for: ", name)
    print("UE - SO = ", total_system_travel_time_equilibrium - total_system_travel_time_optimal)
    
    pairs = []
    read_input(f'./assignments/{name}_result_SO.txt', pairs)
    calculate_routes(pairs)
    write_results(f'./assignments/{name}_result_SO_routes.txt', pairs)
    