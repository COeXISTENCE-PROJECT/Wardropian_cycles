import math
import csv
from functools import reduce
from utils import Route, Agent



def prep_data(route_data):
    '''
    Prepare the data for the simulation - round q to the nearest integer
    
    Parameters:
        route_data (list of tuple): Each tuple represents a route as (flow, time), where flow is the number of agents that can take this route, and time is the associated time.
        recommended to use the Route object from utils.py
        
    Returns:
        tuple: A tuple containing the total number of agents needed and the route data.
    '''
    route_data = [(round(r.flow), r.time) for r in route_data]
    # calculate the total number of agents needed
    total_agents = sum(q for q, _ in route_data)
    return total_agents, route_data

def run_simulation(num_agents, route_data, thresholds=[], max_steps=10000, eps=0, debug=False):
    """
    Runs the simulation for a given number of agents and route data.

    Parameters:
        num_agents (int): The number of agents.
        route_data (list of Route object): Each tuple represents a route as (flow, time), where flow is the number of agents that can take this route, and time is the associated time.
        thresholds (list of float): A list of convergence thresholds other than absolute convergence. Default is an empty list.
        max_steps (int): The maximum number of simulation steps. Default is 10,000.

    Returns:
        dict: A dictionary containing the history of agent positions, mean times, variances and fairness for each step.
    """
    agents = [Agent(i) for i in range(num_agents)]
    routes = [Route(j, q, t) for j, (q, t) in enumerate(route_data)]
    history = []
    mean = []
    variance = []
    fairness = []
    fairness_norm = []
    almost_convergence = [-1] * len(thresholds)

    def prepare_routes():
        # min_time = min(routes, key=lambda r: r.time).time
        # for route in routes:
        #     route.time -= min_time
        routes.sort()

    def assign_routes(routes, agents):
        assigned_routes = [0] * len(agents)
        idx = 0
        for i in range(len(routes)):
            for j in range(routes[i].flow):
                if idx < len(agents):
                    assigned_routes[idx] = i
                    idx += 1
        return assigned_routes

    def simulation_step():
        assigned_routes = assign_routes(routes, agents)

        for i in range(len(agents)):
            agents[i].add_time(routes[assigned_routes[i]].time, mean_time)

        agent_history = [0] * len(agents)

        for i in range(len(agents)):
            agent_history[agents[i].id] = assigned_routes[i]
        if debug:
            for agent in agents:
                print(f"Agent {agent.id} has time {agent.sum_time}")
        step_mean = sum(agent.sum_time for agent in agents) / len(agents)
        step_variance = sum((agent.sum_time - step_mean) ** 2 for agent in agents) / len(agents)
        step_fairness = sum(pow(agent.sum_deviation, 2) for agent in agents) / (len(agents))
        history.append(agent_history)
        mean.append(step_mean)
        variance.append(step_variance)
        fairness.append(step_fairness)
        fairness_norm.append(step_fairness /fairness[0]) # normalize fairness to make it comparable
        if(len(mean) != len(variance)):
            print("Error: mean and variance are not the same length")
            print("Mean: ", len(mean))
            print("Variance: ", len(variance))
        agents.sort()

    def check_convergence(eps, cntr):
        min_time = min(agents, key=lambda a: a.sum_time).sum_time
        max_time = max(agents, key=lambda a: a.sum_time).sum_time
        max_diff = max_time - min_time
        if max_diff > eps:
            if debug:
                print(f"Not converged yet! Max diff: {max_diff}")
            return False
        if debug:
            print(f"Converged in {cntr} steps!")
        return True
    
    def norm_fairness_convergence(eps):
        # if fairness is less than eps
        if fairness_norm[-1] < eps:
            return True
        return False
    
    # Prepare and run the simulation
    prepare_routes()
    cntr = 0
    converged = False
    convergence_iter = -1
    mean_time = sum(route.flow * route.time for route in routes) / num_agents
    while cntr < max_steps:
        cntr += 1
        simulation_step()
        if cntr % 100 == 0 and debug:
            print(f"Step {cntr} stats:")
            for agent in agents:
                print(f"Agent {agent.id} has time {agent.sum_time}")
            
        for i, threshold in enumerate(thresholds):
            if almost_convergence[i] == -1 and norm_fairness_convergence(threshold):
                almost_convergence[i] = cntr

        if check_convergence(eps, cntr):
            if not converged:
                convergence_iter = cntr
            converged = True

    # Return the simulation results
    return {
        "convergence": (converged, convergence_iter),
        "history": history,
        "mean": mean,
        "variance": variance,
        "fairness": fairness,
        "fairness_norm": fairness_norm,
        "almost_convergence": almost_convergence
    }

# Example usage of the run_simulation function
if __name__ == "__main__":
    num_agents = 9
    route_data = [(2, 15.0), (3, 14.0), (4, 9.0)]
    avg_time = sum(q * t for q, t in route_data) / num_agents
    thresholds = [0.3, 0.1, 0.05]
    results = run_simulation(num_agents, route_data, thresholds,max_steps=10000, eps=0.1)

    # Output the results
    print("Simulation Results:")
    print("History:", results["history"])
    print("Mean:", results["mean"])
    print("Variance:", results["variance"])
    print("Fairness:", results["fairness"])
    print("Converged:", results["convergence"][0])  
    print("Convergence thresholds:", results["almost_convergence"])
    print("average time", avg_time)