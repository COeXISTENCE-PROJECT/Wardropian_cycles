import heapq
import time

import networkx as nx
import scipy
import matplotlib.pyplot as plt

from network_import import *
from utils import PathUtils, BPRcostFunction, constantCostFunction, greenshieldsCostFunction
from typesFW import *
# TODO: zmienic input Ue na ścieżki, a nie krawędzie - czas ma być całościowy, nie krawędziowy.


def DijkstraHeap(origin, network: FlowTransportNetwork):
    """
    Calcualtes shortest path from an origin to all other destinations.
    The labels and preds are stored in node instances.
    """
    for n in network.nodeSet:
        network.nodeSet[n].label = np.inf
        network.nodeSet[n].pred = None
    network.nodeSet[origin].label = 0.0
    network.nodeSet[origin].pred = None
    SE = [(0, origin)]
    while SE:
        currentNode = heapq.heappop(SE)[1]
        currentLabel = network.nodeSet[currentNode].label
        for toNode in network.nodeSet[currentNode].outLinks:
            link = (currentNode, toNode)
            newNode = toNode
            newPred = currentNode
            existingLabel = network.nodeSet[newNode].label
            newLabel = currentLabel + network.linkSet[link].cost
            if newLabel < existingLabel:
                heapq.heappush(SE, (newLabel, newNode))
                network.nodeSet[newNode].label = newLabel
                network.nodeSet[newNode].pred = newPred


def updateTravelTime(network: FlowTransportNetwork, optimal: bool = False, costFunction=BPRcostFunction):
    """
    This method updates the travel time on the links with the current flow
    """
    for l in network.linkSet:
        network.linkSet[l].cost = costFunction(optimal,
                                               network.linkSet[l].fft,
                                               network.linkSet[l].alpha,
                                               network.linkSet[l].flow,
                                               network.linkSet[l].capacity,
                                               network.linkSet[l].beta,
                                               network.linkSet[l].length,
                                               network.linkSet[l].speedLimit
                                               )


def findAlpha(x_bar, network: FlowTransportNetwork, optimal: bool = False, costFunction=BPRcostFunction, verbose=False):
    """
    This uses unconstrained optimization to calculate the optimal step size required
    for Frank-Wolfe Algorithm
    """

    def df(alpha):
        assert 0 <= alpha <= 1
        sum_derivative = 0  # this line is the derivative of the objective function.
        for l in network.linkSet:
            tmpFlow = alpha * x_bar[l] + (1 - alpha) * network.linkSet[l].flow
            tmpCost = costFunction(optimal,
                                   network.linkSet[l].fft,
                                   network.linkSet[l].alpha,
                                   tmpFlow,
                                   network.linkSet[l].capacity,
                                   network.linkSet[l].beta,
                                   network.linkSet[l].length,
                                   network.linkSet[l].speedLimit
                                   )
            sum_derivative = sum_derivative + (x_bar[l] - network.linkSet[l].flow) * tmpCost
        return sum_derivative
    # case when both signs are the same
    if verbose and df(0) * df(1) > 0:
        print(f"Both signs are {"positive" if df(0) > 0 else "negative"}")
        if df(0) > 0:
            return 0
        else:
            return 1
        
    sol = scipy.optimize.root_scalar(df, x0=np.array([0.5]), bracket=(0, 1))
    assert 0 <= sol.root <= 1
    return sol.root

def checkConstraints(x_bar, x_bar_od, network: FlowTransportNetwork, alpha: float = 1.0, optimal: bool = False, costFunction=BPRcostFunction, verbose=False) -> bool:
    """
    This method checks if the assignment alpha * x_bar + (1 - alpha) * network.linkSet[l].flow satisfies the CSO constraint
    """
    # for each OD pair check if the CSO constraint is satisfied - if not return False
    # CSO constraint - for each OD pair sum of time on links should be less than or equal to the Q_od * T_od^UE where Q_od is the demand and T_od^UE is the travel time in the UE assignment
    
    odTimes = {od: 0.0 for od in network.tripSet}
    for l in network.linkSet:
        flow = alpha * x_bar[l] + (1 - alpha) * network.linkSet[l].flow
        tmpTime = costFunction(False,
                               network.linkSet[l].fft,
                                   network.linkSet[l].alpha,
                                   flow,
                                   network.linkSet[l].capacity,
                                   network.linkSet[l].beta,
                                   network.linkSet[l].length,
                                   network.linkSet[l].speedLimit
                                   )
        for od in network.tripSet:
            od_flow = alpha * x_bar_od[l + od] + (1 - alpha) * network.linkSetWithOD[l + od].flow
            odTimes[od] += od_flow * tmpTime
        
    for od in network.tripSet:
        if network.tripSet[od].demand == 0:
            continue
        # print(od, odTimes[od], network.tripTime[od])
        if odTimes[od] > network.tripTime[od]:
            return False
    return True


def makeAlphaFeasible(x_bar, x_bar_od, network: FlowTransportNetwork, alpha: float, optimal: bool = True, costFunction=BPRcostFunction, verbose=False):
    """
    This method modifies the x_bar to satisfy the CSO constraint - simple binary search
    """
    
    low = 0
    high = alpha
    if verbose:
        print("Making alpha feasible ", time.time())
    while high - low > 1e-6:
        mid = (low + high) / 2
        if checkConstraints(x_bar, x_bar_od, network, mid, optimal, costFunction, verbose):
            high = mid
        else:
            low = mid
    return high

def tracePreds(dest, network: FlowTransportNetwork):
    """
    This method traverses predecessor nodes in order to create a shortest path
    """
    prevNode = network.nodeSet[dest].pred
    spLinks = []
    while prevNode is not None:
        spLinks.append((prevNode, dest))
        dest = prevNode
        prevNode = network.nodeSet[dest].pred
    return spLinks


def loadAON(network: FlowTransportNetwork, computeXbar: bool = True):
    """
    This method produces auxiliary flows for all or nothing loading.
    """
    x_bar = {l: 0.0 for l in network.linkSet}
    x_bar_od = {l: 0.0 for l in network.linkSetWithOD}
    SPTT = 0.0
    for r in network.originZones:
        DijkstraHeap(r, network=network)
        for s in network.zoneSet[r].destList:
            dem = network.tripSet[r, s].demand

            if dem <= 0:
                continue

            SPTT = SPTT + network.nodeSet[s].label * dem

            if computeXbar and r != s:
                for spLink in tracePreds(s, network):
                    x_bar[spLink] = x_bar[spLink] + dem
                    x_bar_od[spLink + (r, s)] = dem
    return SPTT, x_bar, x_bar_od


def readDemand(demand_df: pd.DataFrame, network: FlowTransportNetwork, CSO: bool = False):
    for index, row in demand_df.iterrows():

        init_node = str(int(row["init_node"]))
        term_node = str(int(row["term_node"]))
        demand = row["demand"]

        network.tripSet[init_node, term_node] = Demand(init_node, term_node, demand)
        if init_node not in network.zoneSet:
            network.zoneSet[init_node] = Zone(init_node)
        if term_node not in network.zoneSet:
            network.zoneSet[term_node] = Zone(term_node)
        if term_node not in network.zoneSet[init_node].destList:
            network.zoneSet[init_node].destList.append(term_node)

        for link in network.linkSet:
            for od in network.tripSet:
                # print(link, od)
                # print(network.linkSet[link])
                if link + od not in network.linkSetWithOD:
                    network.linkSetWithOD[link + od] = Link(init_node=network.linkSet[link].init_node,
                                                            term_node=network.linkSet[link].term_node,
                                                            capacity=network.linkSet[link].capacity,
                                                            length=network.linkSet[link].length,
                                                            fft=network.linkSet[link].fft,
                                                            b=network.linkSet[link].alpha,
                                                            power=network.linkSet[link].beta,
                                                            speed_limit=network.linkSet[link].speedLimit,
                                                            toll=network.linkSet[link].toll,
                                                            linkType=network.linkSet[link].linkType
                                                            )
    print(len(network.zoneSet), "OD zones")


def readNetwork(network_df: pd.DataFrame, UE_od_link_df: pd.DataFrame, UE_trips_df: pd.DataFrame, network: FlowTransportNetwork):
    for index, row in network_df.iterrows():

        init_node = str(int(row["init_node"]))
        term_node = str(int(row["term_node"]))
        capacity = row["capacity"]
        length = row["length"]
        free_flow_time = row["free_flow_time"]
        b = row["b"]
        power = row["power"]
        speed = row["speed"]
        toll = row["toll"]
        link_type = row["link_type"]

        network.linkSet[init_node, term_node] = Link(init_node=init_node,
                                                     term_node=term_node,
                                                     capacity=capacity,
                                                     length=length,
                                                     fft=free_flow_time,
                                                     b=b,
                                                     power=power,
                                                     speed_limit=speed,
                                                     toll=toll,
                                                     linkType=link_type
                                                     )
        if init_node not in network.nodeSet:
            network.nodeSet[init_node] = Node(init_node)
        if term_node not in network.nodeSet:
            network.nodeSet[term_node] = Node(term_node)
        if term_node not in network.nodeSet[init_node].outLinks:
            network.nodeSet[init_node].outLinks.append(term_node)
        if init_node not in network.nodeSet[term_node].inLinks:
            network.nodeSet[term_node].inLinks.append(init_node)

    print(len(network.nodeSet), "nodes")
    print(len(network.linkSet), "links")
    
    if UE_od_link_df is not None:
        print("Reading the UE link flows")
        ueFlows = {}
        for index, row in UE_od_link_df.iterrows():
            origin = str(int(row["origin"]))
            destination = str(int(row["destination"]))
            link_origin = str(int(row["link_origin"]))
            link_destination = str(int(row["link_destination"]))
            flow = row["flow"]
            link = (link_origin, link_destination)
            od = (origin, destination)
            if link not in ueFlows:
                ueFlows[link] = 0.0
            ueFlows[link] += flow
            network.linkSetWithOD[link+od] = Link(init_node=network.linkSet[link].init_node,
                                                            term_node=network.linkSet[link].term_node,
                                                            capacity=network.linkSet[link].capacity,
                                                            length=network.linkSet[link].length,
                                                            fft=network.linkSet[link].fft,
                                                            b=network.linkSet[link].alpha,
                                                            power=network.linkSet[link].beta,
                                                            speed_limit=network.linkSet[link].speedLimit,
                                                            toll=network.linkSet[link].toll,
                                                            linkType=network.linkSet[link].linkType
                                                            )
            network.linkSetWithOD[link+od].flow = flow
        network.ueFlows = ueFlows
    if UE_trips_df is not None:
        print("Reading the UE travel times")
        tripTime = {}
        for index, row in UE_trips_df.iterrows():
            
            init_node = str(int(row["init_node"]))
            term_node = str(int(row["term_node"]))
            UE_time = row["travelTime"]
            UE_flow = row["flow"]
            tripTime[init_node, term_node] = UE_time * UE_flow # total time on the link weighted by the flow
        network.tripTime = tripTime


def get_TSTT(network: FlowTransportNetwork, costFunction=BPRcostFunction, use_max_capacity: bool = True):
    TSTT = round(sum([network.linkSet[a].flow * costFunction(optimal=False,
                                                             fft=network.linkSet[
                                                                 a].fft,
                                                             alpha=network.linkSet[
                                                                 a].alpha,
                                                             flow=network.linkSet[
                                                                 a].flow,
                                                             capacity=network.linkSet[
                                                                 a].max_capacity if use_max_capacity else network.linkSet[
                                                                 a].capacity,
                                                             beta=network.linkSet[
                                                                 a].beta,
                                                             length=network.linkSet[
                                                                 a].length,
                                                             maxSpeed=network.linkSet[
                                                                 a].speedLimit
                                                             ) for a in
                      network.linkSet]), 9)
    return TSTT


def assignment_loop(network: FlowTransportNetwork,
                    algorithm: str = "FW",
                    systemOptimal: bool = False,
                    costFunction=BPRcostFunction,
                    accuracy: float = 0.001,
                    maxIter: int = 1000,
                    maxTime: int = 60,
                    verbose: bool = True,
                    CSO: bool = False
                    ) -> float:
    """
    For explaination of the algorithm see Chapter 7 of:
    https://sboyles.github.io/blubook.html
    PDF:
    https://sboyles.github.io/teaching/ce392c/book.pdf
    """
    if not CSO:
        network.reset_flow()
    else:
        network.set_UE_flow()
        updateTravelTime(network=network,
                         optimal=systemOptimal,
                         costFunction=costFunction)
        
    iteration_number = 1
    gap = np.inf
    TSTT = np.inf
    assignmentStartTime = time.time()

    # Check if desired accuracy is reached
    while gap > accuracy:

        # Get x_bar through all-or-nothing assignment
        _, x_bar, x_bar_od = loadAON(network=network)

        if algorithm == "MSA" or iteration_number == 1:
            alpha = (1 / iteration_number)
        elif algorithm == "FW":
            # If using Frank-Wolfe determine the step size alpha by solving a nonlinear equation
            alpha = findAlpha(x_bar,
                              network=network,
                              optimal=systemOptimal,
                              costFunction=costFunction,
                              verbose=verbose)
            
            if CSO:
                # check if the CSO constraint is satisfied, else binary search for the feasible alpha
                if not checkConstraints(x_bar, x_bar_od, network, alpha, systemOptimal, costFunction, verbose):
                    alpha = makeAlphaFeasible(x_bar, x_bar_od, network, alpha, systemOptimal, costFunction, verbose)
                    if verbose:
                        print("Alpha made feasible:", alpha, " ", time.time())
        else:
            print("Terminating the program.....")
            print("The solution algorithm ", algorithm, " does not exist!")
            raise TypeError('Algorithm must be MSA or FW')

        # Condition for too small alpha
        if CSO and alpha < 1e-6:
            print("Alpha too small, reached the boundary of the constraint, terminating the assignment")
            return TSTT
        # Apply flow improvement
        for l in network.linkSet:
            network.linkSet[l].flow = alpha * x_bar[l] + (1 - alpha) * network.linkSet[l].flow
            for od in network.tripSet:
                network.linkSetWithOD[l + od].flow = alpha * x_bar_od[l + od] + (1 - alpha) * network.linkSetWithOD[l + od].flow
        # Compute the new travel time
        updateTravelTime(network=network,
                         optimal=systemOptimal,
                         costFunction=costFunction)

        # Compute the relative gap
        SPTT, _, _ = loadAON(network=network, computeXbar=False)
        SPTT = round(SPTT, 9)
        TSTT = round(sum([network.linkSet[a].flow * network.linkSet[a].cost for a in
                          network.linkSet]), 9)

        # print(TSTT, SPTT, "TSTT, SPTT, Max capacity", max([l.capacity for l in network.linkSet.values()]))
        gap = (TSTT / SPTT) - 1
        if gap < 0:
            print("Error, gap is less than 0, this should not happen")
            print("TSTT", "SPTT", TSTT, SPTT)

            # Uncomment for debug

            # print("Capacities:", [l.capacity for l in network.linkSet.values()])
            # print("Flows:", [l.flow for l in network.linkSet.values()])

        # Compute the real total travel time (which in the case of system optimal rounting is different from the TSTT above)
        TSTT = get_TSTT(network=network, costFunction=costFunction)

        iteration_number += 1
        writeResults(
            network=network,
            output_file=f'./testing/{iteration_number}_result.txt',
            costFunction=costFunction,
            systemOptimal=systemOptimal,
            verbose=True,
            graph=False
        )
        
        if iteration_number % 100 == 0 and verbose:
            print("Iteration number:", iteration_number, "Current gap:", round(gap, 5))
        if iteration_number > maxIter:
            if verbose:
                print(
                    "The assignment did not converge to the desired gap and the max number of iterations has been reached")
                print("Assignment took", round(time.time() - assignmentStartTime, 5), "seconds")
                print("Current gap:", round(gap, 5))
            return TSTT
        if time.time() - assignmentStartTime > maxTime:
            if verbose:
                print("The assignment did not converge to the desired gap and the max time limit has been reached")
                print("Assignment did ", iteration_number, "iterations")
                print("Current gap:", round(gap, 5))
            return TSTT

    if verbose:
        print("Assignment converged in ", iteration_number, "iterations")
        print("Assignment took", round(time.time() - assignmentStartTime, 5), "seconds")
        print("Current gap:", round(gap, 5))

    return TSTT


def writeResults(network: FlowTransportNetwork, output_file: str, costFunction=BPRcostFunction,
                 systemOptimal: bool = False, verbose: bool = True, graph: bool = False):
    outFile = open(output_file, "w")
    TSTT = get_TSTT(network=network, costFunction=costFunction)
    if verbose:
        print("\nTotal system travel time:", f'{TSTT} secs')
    tmpOut = "Total Travel Time:\t" + str(TSTT)
    outFile.write(tmpOut + "\n")
    tmpOut = "Cost function used:\t" + BPRcostFunction.__name__
    outFile.write(tmpOut + "\n")
    tmpOut = ["User equilibrium (UE) or system optimal (SO):\t"] + ["SO" if systemOptimal else "UE"]
    outFile.write("".join(tmpOut) + "\n\n")
    tmpOut = "init_node\tterm_node\tflow\ttravelTime"
    outFile.write(tmpOut + "\n")
    for i in network.linkSet:
        tmpOut = str(network.linkSet[i].init_node) + "\t" + str(
            network.linkSet[i].term_node) + "\t" + str(
            network.linkSet[i].flow) + "\t" + str(costFunction(False,
                                                               network.linkSet[i].fft,
                                                               network.linkSet[i].alpha,
                                                               network.linkSet[i].flow,
                                                               network.linkSet[i].max_capacity,
                                                               network.linkSet[i].beta,
                                                               network.linkSet[i].length,
                                                               network.linkSet[i].speedLimit
                                                               ))
        outFile.write(tmpOut + "\n")
        
    outFile.close()
    output_file = output_file.replace(".txt", "_OD_pairs.txt")
    
    
    outFile = open(output_file,"w")
    
    outFile.write("OD PAIRS\n")
    
    outFile.write("init_node\tterm_node\tdemand\n")
    outFile.write("init_node\tterm_node\tflow\ttravelTimeOnLink\n")
    
    for od in network.tripSet:
        tmpOut = str(od[0]) + "\t" + str(od[1]) + "\t" + str(network.tripSet[od].demand)
        outFile.write(tmpOut + "\n")
        for i in network.linkSet:
            if network.linkSetWithOD[i + od].flow == 0.0:
                continue
            tmpOut = str(network.linkSet[i].init_node) + "\t" + str(
                network.linkSet[i].term_node) + "\t" + str(
                network.linkSetWithOD[i + od].flow) + "\t" + str(costFunction(False,
                                                                   network.linkSet[i].fft,
                                                                   network.linkSet[i].alpha,
                                                                   network.linkSet[i].flow,
                                                                   network.linkSet[i].max_capacity,
                                                                   network.linkSet[i].beta,
                                                                   network.linkSet[i].length,
                                                                   network.linkSet[i].speedLimit
                                                                   ))
            outFile.write(tmpOut + "\n")
        outFile.write("\n")
    
    if graph:
        # for each OD pair draw a graph with weights as a flow
        for od in network.tripSet:
            G = network.to_networkx()
            for i in network.linkSet:
                G.add_edge(network.linkSet[i].init_node, network.linkSet[i].term_node, weight=round(network.linkSetWithOD[i + od].flow,2))
            edge_labels = nx.get_edge_attributes(G, 'weight')
            # filter out the edges with 0 flow
            edge_labels = {k: v for k, v in edge_labels.items() if v > 0}
            nx.draw(G, with_labels=True)
            nx.draw_networkx_edge_labels(G, pos=nx.spring_layout(G), edge_labels=edge_labels)
            plt.show()


def load_network(net_file: str,
                 demand_file: str = None,
                 UE_link_file: str = None,
                 UE_trip_file: str = None,
                 force_net_reprocess: bool = False,
                 verbose: bool = True,
                 CSO: bool = False
                 ) -> FlowTransportNetwork:
    readStart = time.time()

    if demand_file is None:
        demand_file = '_'.join(net_file.split("_")[:-1] + ["trips.tntp"])

    net_name = net_file.split("/")[-1].split("_")[0]

    if verbose:
        print(f"Loading network {net_name}...")

    net_df, demand_df, UE_od_link_df, UE_trips_df = import_network(
        net_file,
        demand_file,
        UE_link_file,
        UE_trip_file,
        force_reprocess=force_net_reprocess
    )

    network = FlowTransportNetwork()

    readNetwork(net_df, UE_od_link_df, UE_trips_df, network=network)
    readDemand(demand_df, network=network, CSO=CSO)

    network.originZones = set([k[0] for k in network.tripSet])

    if verbose:
        print("Network", net_name, "loaded")
        print("Reading the network data took", round(time.time() - readStart, 2), "secs\n")

    return network


def computeAssignment(net_file: str,
                      demand_file: str = None,
                      algorithm: str = "FW",  # FW or MSA
                      costFunction=BPRcostFunction,
                      systemOptimal: bool = False,
                      accuracy: float = 0.0001,
                      maxIter: int = 1000,
                      maxTime: int = 60,
                      results_file: str = None,
                      force_net_reprocess: bool = False,
                      verbose: bool = True,
                      CSO: tuple = (False, None, None) # (bool, str, str)
                      ) -> float:
    """
    This is the main function to compute the user equilibrium UE (default) or system optimal (SO) traffic assignment
    All the networks present on https://github.com/bstabler/TransportationNetworks following the tntp format can be loaded


    :param net_file: Name of the network (net) file following the tntp format (see https://github.com/bstabler/TransportationNetworks)
    :param demand_file: Name of the demand (trips) file following the tntp format (see https://github.com/bstabler/TransportationNetworks), leave None to use dafault demand file
    :param algorithm:
           - "FW": Frank-Wolfe algorithm (see https://en.wikipedia.org/wiki/Frank%E2%80%93Wolfe_algorithm)
           - "MSA": Method of successive averages
           For more information on how the algorithms work see https://sboyles.github.io/teaching/ce392c/book.pdf
    :param costFunction: Which cost function to use to compute travel time on edges, currently available functions are:
           - BPRcostFunction (see https://rdrr.io/rforge/travelr/man/bpr.function.html)
           - greenshieldsCostFunction (see Greenshields, B. D., et al. "A study of traffic capacity." Highway research board proceedings. Vol. 1935. National Research Council (USA), Highway Research Board, 1935.)
           - constantCostFunction
    :param systemOptimal: Wheather to compute the system optimal flows instead of the user equilibrium
    :param accuracy: Desired assignment precision gap
    :param maxIter: Maximum nuber of algorithm iterations
    :param maxTime: Maximum seconds allowed for the assignment
    :param results_file: Name of the desired file to write the results,
           by default the result file is saved with the same name as the input network with the suffix "_flow.tntp" in the same folder
    :param force_net_reprocess: True if the network files should be reprocessed from the tntp sources
    :param verbose: print useful info in standard output
    :param CSO: tuple (bool, str, str) where the first element is True if the CSO constraint should be applied, the second element is the path to the UE initial flows, while the third is the travel time of trips in UE assignment
    :return: Totoal system travel time
    """

    network = load_network(net_file=net_file, demand_file=demand_file, UE_link_file=CSO[1], UE_trip_file=CSO[2], verbose=verbose, force_net_reprocess=force_net_reprocess, CSO=CSO[0])

    if verbose:
        print("Computing assignment...")
    TSTT = assignment_loop(network=network, algorithm=algorithm, systemOptimal=systemOptimal, costFunction=costFunction,
                           accuracy=accuracy, maxIter=maxIter, maxTime=maxTime, verbose=verbose, CSO=CSO[0])

    if results_file is None:
        results_file = '_'.join(net_file.split("_")[:-1] + ["flow.tntp"])

    writeResults(network=network,
                 output_file=results_file,
                 costFunction=costFunction,
                 systemOptimal=systemOptimal,
                 verbose=verbose,
                 graph=False)

    return TSTT


if __name__ == '__main__':

    # This is an example usage for calculating System Optimal and User Equilibrium with Frank-Wolfe

    net_file = str(PathUtils.sioux_falls_net_file )
    name = net_file.split("/")[-1].split("_")[0]
    # total_system_travel_time_optimal = computeAssignment(net_file=net_file,
                                                         
    #                                                      algorithm="FW",
    #                                                      costFunction=BPRcostFunction,
    #                                                      systemOptimal=True,
    #                                                      verbose=True,
    #                                                      accuracy=0.0001,
    #                                                      maxIter=10000,
    #                                                      maxTime=6000000,results_file=f'./assignments/{name}_result_SO.txt',force_net_reprocess=True)

    total_system_travel_time_optimal_CSO = computeAssignment(net_file=net_file,
                                                             algorithm="FW",
                                                                costFunction=BPRcostFunction,
                                                                systemOptimal=True,
                                                                verbose=True,
                                                                accuracy=0.0001,
                                                                maxIter=100,
                                                                maxTime=6000000,
                                                                results_file=f'./assignments/{name}_result_SO_CSO.txt',
                                                                force_net_reprocess=True,
                                                                CSO=(True, f'./processed_networks/{name}_UE_OD_pairs.csv', f'./processed_networks/{name}_trips_UE.csv'))
    
    print("CSO - SO = ", total_system_travel_time_optimal_CSO, 1268541.494860965, total_system_travel_time_optimal_CSO - 1268541.494860965)
    
    # total_system_travel_time_equilibrium = computeAssingment(net_file=net_file,
    #                                                          algorithm="FW",
    #                                                          costFunction=BPRcostFunction,
    #                                                          systemOptimal=False,
    #                                                          verbose=True,
    #                                                          accuracy=0.00001,
    #                                                          maxIter=10000,
    #                                                          maxTime=6000000, results_file=f'../assignments/{name}_result_UE.txt')

    # print("UE - SO = ", total_system_travel_time_equilibrium - total_system_travel_time_optimal)