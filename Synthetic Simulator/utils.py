import math
from scipy.optimize import minimize
from functools import partial
from enum import Enum


def BPRCostFunction(
    q: float, t0: float, qmax: float, alpha: float = 0.15, beta: float = 4, q_base: float = 0
) -> float:
    """Bureau of Public Roads (BPR) cost function for travel time"""
    if qmax == 0:
        return float("inf")  # If capacity is zero, the cost is infinite
    return t0 * (1 + alpha * ((q+q_base) / qmax) ** beta)


def findUE(q: float, routes: list, debug: bool = False) -> tuple:
    """Finds User Equilibrium (UE) flow assignment"""
    n = len(routes)

    # Decision variables: n flows + 1 extra variable for equilibrium travel time (T)
    def objective(x):
        flows = x[:-1]  # First n elements are flows
        T = x[-1]  # Last element is equilibrium travel time
        return sum(
            [(routes[i](flows[i]) - T) ** 2 for i in range(n)]
        )  # Enforce equal travel times

    # Constraint: sum of x_i = q
    def flow_constraint(x):
        return sum(x[:-1]) - q  # Ignore last variable (T)

    # Bounds: non-negative flows and T unrestricted
    bounds = [(0, q) for _ in range(n)] + [
        (None, None)
    ]  # Last variable (T) is unbounded

    # Initial guess: equal flow split, with an arbitrary T guess
    x0 = [q / n] * n + [1]  # Last element is the initial guess for T

    # Optimization
    res = minimize(
        objective, x0, constraints={"type": "eq", "fun": flow_constraint}, bounds=bounds
    )

    if debug:
        print("UE Result:", res)
    
    

    return (res.x[:-1], res.fun)


def findSO(q: float, routes: list, debug: bool = False) -> tuple:
    """Finds Social Optimum (SO) flow assignment"""

    n = len(routes)

    # Objective function: minimize total travel time
    def objective(x):
        return sum([routes[i](x[i]) * x[i] for i in range(n)])  # Total travel time

    # Constraint: sum of x_i = q
    def constraint(x):
        return sum(x) - q

    # Bounds: non-negative flows
    bounds = [(0, q) for _ in range(n)]

    # Initial guess: equal split
    x0 = [q / n] * n

    # Optimization
    res = minimize(
        objective, x0, constraints={"type": "eq", "fun": constraint}, bounds=bounds
    )

    if debug:
        print("SO Result:", res)

    return (res.x, res.fun)


if __name__ == "__main__":
    # Rafal's example :)
    t0 = 5
    t1 = 15
    qmax1 = 500
    qmax2 = 800
    q = 1000
    alpha = 1
    beta = 2

    # Fixing lambda function issue using partial
    routes = [
        partial(BPRCostFunction, t0, qmax1, alpha=alpha, beta=beta),
        partial(BPRCostFunction, t1, qmax2, alpha=alpha, beta=beta),
    ]

    ue_flows = findUE(q, routes)
    so_flows = findSO(q, routes)

    print("UE Flows:", ue_flows)
    print("SO Flows:", so_flows)


class VehicleType(Enum):
    HDV = 1
    CAV = 2
