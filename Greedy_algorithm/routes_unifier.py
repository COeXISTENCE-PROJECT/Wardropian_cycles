# read routes from the file, remove path and unify flow of the routes of equal time

import numpy as np
from utils import unify_paths



def read_input(filename: str, pairs: list):
    od_pairs = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        # skip the 2 lines of the header
        lines = lines[2:]
        i = 0
        while i < len(lines):
            origin, destination, flow = lines[i].split()
            flow = float(flow)
            # read paths
            paths = []
            for j in range(i+1, len(lines)):
                path = lines[j]
                if path == '\n':
                    i = j + 1
                    break
                time, flow, path = path.split()
                time = float(time)
                flow = float(flow)
                paths.append((time, flow))
            
            # unify paths with equal time
            paths = unify_paths(paths)
        
        od_pairs.append((origin, destination, flow, paths))
    return od_pairs

def write_results(filename: str, pairs: list):
    with open(filename, 'w') as f:
        for pair in pairs:
            f.write(f'{pair.origin} {pair.destination} {pair.flow}\n')
            for route in pair.routes:
                f.write(f'{route.time} {route.flow} {" ".join(route.path)}\n')
            f.write('\n')
        
    
            