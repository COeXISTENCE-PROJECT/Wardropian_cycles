from functools import partial
import random
from utils import BPRCostFunction, findUE, findSO
from scipy.optimize import minimize

_debug = False

"""
Problem: 
    for a given number of routes and Price of Anarchy, find the travel times and q_max for each route that satisfies PoA
    
    For the simplicity, q_max is randomly generated for each route, optimization is done on t_0s
    
    PoA = (sum of travel times in Nash Equilibrium) / (sum of travel times in Social Optimum)
    
    travel time function: BPRCostFunction(x) = t_0 * (1 + (x / c)^2)
    
    Nash Equilibrium:
        travel times are equal for all routes
        
    Social Optimum:
        sum of travel times is minimized:
            minimize sum(t_i) = minimize sum(t_i_0 * (1 + (x_i / c)^2))
            subject to: sum(x_i) = 1
                        x_i >= 0
"""


def createRoutesForPoA(n: int, PoA: float, C: float) -> tuple:
    """Creates routes for a given number of routes, Price of Anarchy and Congestion"""

    # function to minimize: abs(PoA - (sum of travel times in Nash Equilibrium) / (sum of travel times in Social Optimum))
    def objective(t0) -> float:
        # x = [t_0, ..., t_n]

        # imitialize travel time functions
        routes = [partial(BPRCostFunction, t0=t0[i], qmax=qmax[i]) for i in range(n)]

        # check if proper parameters are passed
        # print("Routes:", routes)

        # find Nash Equilibrium total travel time
        Nash, _ = findUE(1, routes)
        if _debug:
            print("Nash:", Nash)

        sumNash = sum([routes[i](Nash[i]) for i in range(n)])

        # find Social Optimum total travel time
        SO, _ = findSO(1, routes)
        if _debug:
            print("SO:", SO)
        sumSO = sum([routes[i](SO[i]) for i in range(n)])
        if sumSO == 0 or sumNash == 0:
            return float("inf")
        return abs(PoA - sumNash / sumSO)

    # initial guess on t_0s
    x0 = [1] * n
    # initial guess on q_max - sum up to C

    qmax = [random.uniform(0.2, 1) for _ in range(n)]
    sum_qmax = sum(qmax)
    qmax = [q * C / sum_qmax for q in qmax]

    # bounds
    bounds = [(0, 5) for _ in range(n)]

    # optimization
    res = minimize(objective, x0, bounds=bounds)

    if _debug:
        print("PoA Result:", res)

    # print the travel times for Nash Equilibrium and Social Optimum
    t0 = res.x
    routes = [partial(BPRCostFunction, t0=t0[i], qmax=qmax[i]) for i in range(n)]

    if True:
        print("Routes:", routes)
        Nash, _ = findUE(1, routes)
        SO, _ = findSO(1, routes)
        print("Nash:", Nash)
        print("SO:", SO)

        # print the PoA
        sumNash = sum([routes[i](Nash[i]) for i in range(n)])
        sumSO = sum([routes[i](SO[i]) for i in range(n)])

        print("PoA:", sumNash / sumSO)

    return res.x, routes


# Test
if __name__ == "__main__":
    n = 3
    PoA = 1.05

    t_0s, routes = createRoutesForPoA(n, PoA, 1)

    print("Routes:", t_0s)
