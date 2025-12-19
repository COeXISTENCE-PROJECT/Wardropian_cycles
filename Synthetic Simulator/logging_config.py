import logging
import logging.config


def setup_logging():
    # create a logger that will be used in the whole program
    # it will log info about simulation - both the environment and the agents
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logging/simulation.log")],
    )
