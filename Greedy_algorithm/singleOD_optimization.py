import os
import pandas as pd
from utils import OD_pair, PathUtils
from dijkstra_routes import read_input
from assignment_singleOD import computeAssignment, BPRcostFunction
from dijkstra_routes import read_input, write_results, calculate_routes, unify_same_time_paths, average_paths


# workflow of the single OD optimization:
# 1. Calculate the UE for the full network (assume its done in separate script)
# 2. Prepare the input for the assignment_singleOD.py script
#   a) Create the noise flow by removing the flow of the selected OD pair from UE assignment
#   b) Create a trips file for the selected OD pair
#   c) Take the same network file as the one used for the UE assignment
# 3. Calculate the SO for the OD pair using the assignment_singleOD.py script that uses the noise flow
# 4. Plot the results of the assignment

class CSVRecord:
    def __init__(self, origin, destination, link_origin, link_destination, time, flow):
        self.origin = origin
        self.destination = destination
        self.link_origin = link_origin  
        self.link_destination = link_destination
        self.time = time
        self.flow = flow   

def get_noise_flow(UE_OD_file, selected_OD):
    """
    Get the noise flow for the selected OD pair by removing the flow of the selected OD pair from the UE assignment.
    :param UE_file: The file containing the UE assignment
    :param selected_OD: The selected OD pair
    :return: The noise flow dataframe:
    Columns: [init_node, term_node, noise_flow]
    """
    records = []
    
    with open(UE_OD_file, 'r') as file:
        lines = file.readlines()
        lines = lines[3:]
        i = 0
        while i < len(lines):
            origin, destination, demand = lines[i].split()
            demand = float(demand)
            for j in range(i+1, len(lines)):
                edge = lines[j]
                if edge == '\n':
                    i = j + 1
                    break
                # print(edge)
                link_origin, link_destination, flow, time = edge.split()
                flow = float(flow)
                time = float(time)
                records.append(CSVRecord(origin, destination, link_origin, link_destination, time, flow))
                
    # create a DataFrame from the records
    df = pd.DataFrame([record.__dict__ for record in records])
    # remove the flow of the selected OD pair - origin and destination is the same as in the UE assignment
    df = df[~((df['origin'] == str(selected_OD[0])) & (df['destination'] == str(selected_OD[1])))]
    # group by link_origin and link_destination and sum the flow
    df = df.groupby(['link_origin', 'link_destination'])["flow"].sum().reset_index()
    # cast init_node and term_node to int
    df['link_origin'] = df['link_origin'].astype(int)
    df['link_destination'] = df['link_destination'].astype(int)
    return df.rename(columns={"link_origin": "init_node", "link_destination": "term_node", "flow": "noise_flow"})
    # rename the columns


def prepare_network(net_file, UE_OD_file, selected_OD):
    """
    Prepare the network and demand files for the selected OD pair.
    :param net_file: The network file
    :param UE_OD_file: The file containing the UE assignment
    """
    network_file_csv = str(PathUtils.processed_networks_folder / (net_file.split(".")[0].split("/")[-1] + ".csv"))
    # replace _net.csv with _trips.csv at the end of the file name
    demand_file_csv = network_file_csv.replace("_net.csv", "_trips.csv")

    new_network_file_csv = network_file_csv.replace("_net.csv", f"_{selected_OD}_net.csv")
    new_demand_file_csv = demand_file_csv.replace("_trips.csv", f"_{selected_OD}_trips.csv")

    network_df = pd.read_csv(str(network_file_csv),
                             sep='\t')
    demand_df = pd.read_csv(str(demand_file_csv),
                            sep='\t')
    
    noise_flow_df = get_noise_flow(UE_OD_file, selected_OD)
    network_df['init_node'] = network_df['init_node'].astype(int)
    network_df['term_node'] = network_df['term_node'].astype(int)
    network_df = network_df.merge(noise_flow_df, how='left', left_on=['init_node', 'term_node'], right_on=['init_node', 'term_node'])
    network_df['noise_flow'] = network_df['noise_flow'].fillna(0)
    network_df['noise_flow'] = network_df['noise_flow'].astype(int)

    network_df.to_csv(path_or_buf=str(new_network_file_csv),
                      sep='\t',
                      index=False)
    
    # leave in demand_df the selected OD pair
    demand_df = demand_df[(demand_df['init_node'] == selected_OD[0]) & (demand_df['term_node'] == selected_OD[1])]
    demand_df.to_csv(path_or_buf=str(new_demand_file_csv),
                      sep='\t',
                      index=False)
    return new_network_file_csv, new_demand_file_csv


_compute_initial_assignment = True   
_skip_computation = False
    
if __name__ == "__main__":
    net_file = str(PathUtils.berlin_prenzlauberg_center_net_file)
    name = net_file.split("/")[-1].split("_")[0]
    if not _skip_computation:
        if _compute_initial_assignment:
            total_system_travel_time_optimal = computeAssignment(net_file=net_file,
                                                                algorithm="FW",
                                                                costFunction=BPRcostFunction,
                                                                systemOptimal=False,
                                                                verbose=False,
                                                                accuracy=0.000005,
                                                                maxIter=6000,
                                                                maxTime=6000000,results_file=f'./assignments/{name}_result_UE.txt',force_net_reprocess=True)

            print("UE:", total_system_travel_time_optimal)
        pairs_UE = []
        read_input(f'./assignments/{name}_result_UE_OD_pairs.txt', pairs_UE)
        pairs_UE = calculate_routes(pairs_UE)
        pairs_UE = average_paths(pairs_UE)
        write_results(f'./assignments/{name}_result_UE_routes.txt', pairs_UE, 'UE')

        for pairUE in pairs_UE:
            net_file2, demand_file2 = prepare_network(net_file, f'./assignments/{name}_result_UE_OD_pairs.txt', (pairUE.origin, pairUE.destination))
            try:
                total_system_travel_time_equilibrium = computeAssignment(net_file=net_file2,
                                                                        algorithm="FW",
                                                                        costFunction=BPRcostFunction,
                                                                        systemOptimal=True,
                                                                        verbose=True,
                                                                        accuracy=0.000001,
                                                                        maxIter=6000,
                                                                        maxTime=6000000, results_file=f'./assignments/sioux_pairs/{name}_{pairUE.origin}_{pairUE.destination}_result_UE.txt')
                print("Computed for: ", name)
            except Exception as e:
                print(f"Error computing for {pairUE.origin} - {pairUE.destination}: {e}")
                continue
    else:
        # read the results from the files
        pairs_UE = []
        read_input(f'./assignments/{name}_result_UE_OD_pairs.txt', pairs_UE)
        pairs_UE = calculate_routes(pairs_UE)
        pairs_UE = average_paths(pairs_UE)
    

    pairs_SO = []
    for pairSO in pairs_UE:
        pair= []
        try:
            read_input(f'./assignments/sioux_pairs/{name}_{pairSO.origin}_{pairSO.destination}_result_UE_OD_pairs.txt', pair)
        except FileNotFoundError:
            print(f"File not found for {pairSO.origin} - {pairSO.destination}")
            # add empty pair to the list
            pairs_SO.append(OD_pair(pairSO.origin, pairSO.destination, pairSO.flow))
            continue
        pair = calculate_routes(pair)
        pair = unify_same_time_paths(pair)
        print(pair)
        pairs_SO.append(pair[0])

    pairs_UE = []
    read_input(f'./assignments/{name}_result_UE_OD_pairs.txt', pairs_UE)
    pairs_UE = calculate_routes(pairs_UE)
    pairs_UE = average_paths(pairs_UE)

    diff = 0
    diff_percent = 0
    tot_flow = 0

    rows = []
    for pairSO, pairUE in zip(pairs_SO, pairs_UE):
        if pairSO.origin != pairUE.origin or pairSO.destination != pairUE.destination:
            raise ValueError("The origin and destination of the pairs do not match")
        # compare the results
        if len(pairSO.routes) == 1:
            continue
        print(f"Pair: {pairSO.origin} - {pairSO.destination}")
        print(f"SO:")
        sum_flow = 0
        sum_time = 0
        for route in pairSO.routes:
            print(f"Route: {route.path} - {route.time} - {route.flow}")
            sum_flow += route.flow
            sum_time += route.time* route.flow
        if sum_flow == 0:
            print("No flow")
            continue
        print(f"Total flow: {sum_flow}")
        print(f"Average time: {sum_time/sum_flow}")
        print(f"UE:")
        rows.append([pairSO.origin, pairSO.destination, sum_time/sum_flow, pairUE.routes[0].time, pairUE.routes[0].time - sum_time/sum_flow, sum_flow, len(pairSO.routes), [route.time for route in pairSO.routes], [route.flow for route in pairSO.routes]])
        for route in pairUE.routes:
            print(f"Route: {route.path} - {route.time} - {route.flow}")
        print()
        dff = pairUE.routes[0].time - sum_time/sum_flow
        diff += dff * sum_flow
        diff_percent += dff * 100 / (sum_time/sum_flow) * sum_flow
        tot_flow += sum_flow
    
    df = pd.DataFrame(rows, columns=["origin", "destination", "SO_time", "UE_time", "diff", "flow", "SO_routes_num", "SO_routes_time", "SO_routes_flow"])
    df.to_csv(path_or_buf=f'./algorithm_results/single_OD/{name}_OD_to_UE.csv',
                sep=',',
                index=False)
    
    print(f"Total difference: {diff}")
    print(f"Total flow: {tot_flow}")
    print(f"Average difference: {diff/tot_flow}")
    print(f"Average difference percent: {diff_percent/tot_flow}")
