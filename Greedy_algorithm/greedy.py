import math
import csv
from functools import reduce

debug = 0

class Route:
    def __init__(self, id=0, flow=0, time=0.0):
        self.id = id
        self.flow= flow
        self.time = time

    def __lt__(self, other):
        # The route with the highest time is first
        return self.time > other.time


class Agent:
    def __init__(self, id=0):
        self.id = id
        self.sum_time = 0.0

    def add_time(self, time):
        if debug:
            print(f"time adder: agent {self.id} of time {self.sum_time} increases by {time}")
        self.sum_time += time
        self.sum_time = round(self.sum_time * 1000) / 1000

    def __lt__(self, other):
        # The agent with the highest sum of times is first
        return self.sum_time < other.sum_time

def prep_data(route_data):
    # Prepare the data for the simulation - round q to the nearest integer
    # route data is a list of Route objects
    route_data = [(round(r.flow), r.time) for r in route_data]
    # calculate the total number of agents needed
    total_agents = sum(q for q, _ in route_data)
    return total_agents, route_data

def run_simulation(num_agents, route_data, max_steps=10000, eps=0):
    """
    Runs the simulation for a given number of agents and route data.

    Parameters:
        num_agents (int): The number of agents.
        route_data (list of Route object): Each tuple represents a route as (flow, time), where flow is the number of agents that can take this route, and time is the associated time.
        max_steps (int): The maximum number of simulation steps. Default is 10,000.
        eps (float): Convergence threshold. The simulation stops if the maximum difference between agents' times is below this value. Default is 0.

    Returns:
        dict: A dictionary containing the history of agent positions, mean times, and variances for each step.
    """
    agents = [Agent(i) for i in range(num_agents)]
    routes = [Route(j, q, t) for j, (q, t) in enumerate(route_data)]
    history = []
    mean = []
    variance = []

    def prepare_routes():
        min_time = min(routes, key=lambda r: r.time).time
        for route in routes:
            route.time -= min_time
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
            agents[i].add_time(routes[assigned_routes[i]].time)

        agent_history = [0] * len(agents)

        for i in range(len(agents)):
            agent_history[agents[i].id] = assigned_routes[i]

        step_mean = sum(agent.sum_time for agent in agents) / len(agents)
        step_variance = sum((agent.sum_time - step_mean) ** 2 for agent in agents) / len(agents)

        history.append(agent_history)
        mean.append(step_mean)
        variance.append(step_variance)

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

    # Prepare and run the simulation
    prepare_routes()
    cntr = 0
    converged = False
    while not converged and cntr < max_steps:
        cntr += 1
        simulation_step()
        if cntr % 100 == 0 and debug:
            print(f"Step {cntr} stats:")
            for agent in agents:
                print(f"Agent {agent.id} has time {agent.sum_time}")

        if check_convergence(eps, cntr):
            converged = True

    # Return the simulation results
    return {
        "convergence": converged,
        "history": history,
        "mean": mean,
        "variance": variance
    }

# Example usage of the run_simulation function
if __name__ == "__main__":
    num_agents = 5
    route_data = [(2, 10.0), (3, 5.0), (1, 8.0)]
    results = run_simulation(num_agents, route_data, max_steps=10000, eps=0.1)

    # Output the results
    print("Simulation Results:")
    print("History:", results["history"])
    print("Mean:", results["mean"])
    print("Variance:", results["variance"])