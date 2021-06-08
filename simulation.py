from mkl_random.mklrand import choice
from numpy.random.mtrand import sample

from utils import *
from constants import *
import networkx as nx
import pandas as pd
import numpy as np

INCUBATION_PERIOD = 7  # time before symptoms show up, and you become infectious


class Node:
    def __init__(self, susceptible=True, exposed=False, infectious=False, recovered=False):
        self.alive = True
        self.susceptible = susceptible
        self.exposed = exposed
        self.infectious = infectious
        self.recovered = recovered
        self.days_exposed = 0  # how many days

    def infect_healthy(self):
        assert self.alive
        assert not self.recovered

        # expose self
        self.exposed = True

    def simulate_day(self):
        # base conditions
        if not self.alive:
            return

        # handle incubation of virus
        if self.exposed:
            self.days_exposed += 1
            # incubation
            if self.days_exposed > INCUBATION_PERIOD:
                self.infectious = True

        # handle transmission of virus
        if self.infectious:
            self.
        # handle death chance

        # handle recovery chance
        pass


def infect_node(g, n):
    node = g.nodes[n]
    if node.recovered or not node.alive:
        # ignore nodes that have built an immunity
        return
    if not node.exposed:
        node.exposed = True
        node.days_exposed = -1


def simulate_one_step(g: nx.Graph, r0):
    # infect an initial proportion of the population
    n = len(g.nodes)

    initial_infected = choice(list(range(n)), r0 * n)

    pass


def generate_graph() -> nx.Graph:
    """
    Generate a social-network graph to represent a given population.

    :return:
    """
    pass
