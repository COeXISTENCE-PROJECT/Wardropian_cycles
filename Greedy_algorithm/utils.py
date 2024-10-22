from typing import Tuple
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.absolute()


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
_debug = True
ROUND = 2 #

def round_trip_time_and_flow(line: str, precision: int = 2) -> Tuple[int, float, float,float]:
    origin, destination, flow, time = line.split()
    flow = round(float(flow), precision)
    time = round(float(time), precision)
    return (origin, destination, flow, time)
