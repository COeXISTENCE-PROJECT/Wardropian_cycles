#from agent import Agent, CAVGroup, HDVGroup
from PoA_finder import createRoutesForPoA
import logging


verbose = True

logger = logging.getLogger(__name__)


class EpisodeHistory:  # is this a proper way to store the history of the episode? What about transition history?
    """
    Class to store the history of the episode
    """

    def __init__(self, agentsDecision: list, routeTravelTimes: list):
        self.agentsDecision = agentsDecision
        self.routeTravelTimes = routeTravelTimes


class Environment:
    """
    System in our simulation. It is responsible for the following:
    - Initialize all the agents and routes
    - Simulate step by step the route choice
    - Simulate group transition by agents
    """

    def __init__(self, params: dict):
        """
        Initialize the environment

        Params are the following:

        """

        self.history = []
        self.env_params = params["env_params"]
        self.params = params

        # TODO: Finish the initialization of the environment

        #self.__initializeAgents()
        if verbose:
            logging.info("Agents initialized")

        self.__initializeRoutes()
        if verbose:
            logging.info("Routes initialized")


    def __initializeRoutes(self):
        """
        Initialize the routes in the environment

        The routes should preserve the PoA of the system.
        """
        self.n_routes = self.env_params["n_routes"]

        PoA = self.env_params["PoA"]
        congestion = self.env_params["congestion"]

        _, self.routes = createRoutesForPoA(self.n_routes, PoA, congestion)

    def reset(self):
        """
        Reset the environment
        """
        self.__initializeRoutes()

    

    def simulate(self, n_episodes: int):
        """
        Simulate the environment for n_episodes
        """

        scale = self.env_params["time_scales_ratio"]

        for month in range(n_episodes):
            for day in range(scale):
                self.assignmentStep()

            MS, changed = self.transitionStep()

            logging.info(f"Market Share: {MS}, Changed: {changed}")

            if self.__checkConvergence(MS, changed):
                break

        # TODO: add the history of the episode and what to return
