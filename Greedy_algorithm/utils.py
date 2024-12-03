from typing import Tuple
from pathlib import Path
import networkx as nx

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.absolute()


class Agent:
    def __init__(self, id=0):
        self.id = id
        self.sum_time = 0.0
        self.sum_deviation = 0.0

    def add_time(self, time, mean_time):
        self.sum_time += time
        self.sum_time = round(self.sum_time * 1000) / 1000
        self.sum_deviation += time - mean_time

    def __lt__(self, other):
        # The agent with the highest sum of times is first
        return self.sum_time < other.sum_time

class Route:
    def __init__(self, time: float, flow: float, id: int = 0, path: list = []):
        self.time = time
        self.flow = flow
        self.path = path
        self.id = id
        
    def get_num_routes(self):
        return len(self.path)
        
    def __str__(self):
        return f'route: {self.time} {self.flow} {self.path}'

    def __lt__(self, other):
        # The route with the highest time is first
        return self.time > other.time
    
class OD_pair:
    def __init__(self, origin: int, destination: int, flow: float):
        self.origin = int(origin)
        self.destination = int(destination)
        self.flow = flow
        self.graph = {}
        self.routes = []
        
    def add_graph(self, graph: nx.Graph):
        self.graph = graph
    
    def add_routes(self, routes: Route):
        self.routes.append(routes)
    
    def set_routes(self, routes: list):
        self.routes = routes
    
    def recalculate_flow(self):
        self.flow = sum([route.flow for route in self.routes])
    
    def __str__(self):
        return f'pair: {self.origin} {self.destination} {self.flow}'
    

class PathUtils:
    """
    Utils for file names
    """

    # FOLDERS

    # Input netwroks
    input_networks_folder = get_project_root() / "tntp_networks"
    processed_networks_folder = get_project_root() / "processed_networks"

    # FILES

    # Network files
    anaheim_net_file = input_networks_folder / "Anaheim_net.tntp"
    barcelona_net_file = input_networks_folder / "Barcelona_net.tntp"
    braess_net_file = input_networks_folder / "Braess_net.tntp"
    chicago_net_file = input_networks_folder / "ChicagoSketch_net.tntp"
    eastern_massachusetts_net_file = input_networks_folder / "EMA_net.tntp"
    sioux_falls_net_file = input_networks_folder / "SiouxFalls_net.tntp"
    winnipeg_net_file = input_networks_folder / "Winnipeg_net.tntp"
    
    # Demand files
    anaheim_trips_file = input_networks_folder / "Anaheim_trips.tntp"
    barcelona_trips_file = input_networks_folder / "Barcelona_trips.tntp"
    braess_trips_file = input_networks_folder / "Braess_trips.tntp"
    chicago_trips_file = input_networks_folder / "ChicagoSketch_trips.tntp"
    eastern_massachusetts_trips_file = input_networks_folder / "EMA_trips.tntp"
    sioux_falls_trips_file = input_networks_folder / "SiouxFalls_trips.tntp"
    winnipeg_trips_file = input_networks_folder / "Winnipeg_trips.tntp"
    






PATH = '../assignments/'
_debug = False
ROUND = 2 #

def round_trip_time_and_flow(line: str, precision: int = 2) -> Tuple[int, int, float,float]:
    origin, destination, flow, time = line.split()
    origin, destination = int(origin), int(destination)
    flow = round(float(flow), precision)
    time = round(float(time), precision)
    return (origin, destination, flow, time)

def num_of_routes(routes: list) -> int:
    cntr = 0
    for route in routes:
        # calculate number of routes with flow > 1
        if route.flow > 1:
            cntr += 1
    return cntr
