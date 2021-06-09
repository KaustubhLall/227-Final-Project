from icecream import ic
from mkl_random.mklrand import choice, uniform
from numpy.random.mtrand import sample

from utils import *
from constants import *
import networkx as nx
import pandas as pd
import numpy as np


def initialize_graph(g, susceptible=True, exposed=False, infectious=False, recovered=False):
    p = {
        'alive'       : True,
        'susceptible' : susceptible,
        'exposed'     : exposed,
        'infectious'  : infectious,
        'recovered'   : recovered,
        'days_exposed': 0,
        }
    params = {}

    for n in g.nodes:
        params[n] = p

    nx.set_node_attributes(g, params)


def action_recover_node(g, n):
    """Logic to recover a node from terminal state"""
    (g.nodes[n])['infectious'] = False
    (g.nodes[n])['exposed'] = False
    (g.nodes[n])['recovered'] = True


def action_kill_node(g, n):
    """Logic to kill a node which does not survive covid after active duration"""
    assert g.nodes[n]['alive']
    # death logic
    (g.nodes[n])['alive'] = False
    (g.nodes[n])['infectious'] = False
    (g.nodes[n])['exposed'] = False
    (g.nodes[n])['days_exposed'] = -inf


def action_infect_node(g, n, forced=False):
    """Logic to infect a node, generally called by neighbors. Will infect with CHANCE_INFECTION."""
    if g.nodes[n]['recovered'] or not g.nodes[n]['alive']:
        # ignore nodes that have built an immunity
        return
    if not g.nodes[n]['exposed']:
        if forced or ((not forced) and uniform() < CHANCE_INFECTION):
            (g.nodes[n])['exposed'] = True
            (g.nodes[n])['days_exposed'] = -1


def process_exposed_nodes(g, n):
    """Logic to process exposed nodes and make them infectious"""
    if not g.nodes[n]['infectious'] and g.nodes[n]['days_exposed'] > INCUBATION_PERIOD:
        (g.nodes[n])['infectious'] = True


def process_terminal_node(g, n):
    """Logic to process terminal nodes, aka those at the end of the active disease period"""
    if g.nodes[n]['days_exposed'] > ACTIVE_DISEASE_PERIOD:
        # handle recovery and death
        if uniform() < RECOVERY:
            action_kill_node(g, n)
        else:
            action_recover_node(g, n)


def prob_interaction(n1, n2):
    """Probability of a node interacting with another node"""
    return 1


def simulate_one_step(g: nx.Graph):
    """runs one day in a covid-19 simulation"""
    # infect an initial proportion of the population
    for n in g.nodes:
        # increment day if exposed
        node = g.nodes[n]
        if node['exposed']:
            node['days_exposed'] += 1

        # process the node's infection status
        process_exposed_nodes(g, n)

        # process the node's terminal status
        process_terminal_node(g, n)

        # process the node's chance to infect its neighbors
        if node['infectious']:
            [action_infect_node(g, x) for x in g.neighbors(n) if uniform() < prob_interaction(x, node)]

    disg(g)
    return g


def disg(g):
    for n in g.nodes:
        print(g.nodes[n], n)


def simulate(r0, steps=100):
    """Driver function to run a simulation for a given number of days with given input parameters"""
    g = generate_graph(10, 1)

    # initialize the graph
    initialize_graph(g)

    N = len(g.nodes)
    initial_infected = choice(list(range(N)), int(r0 * N))
    if len(initial_infected) == 0:
        initial_infected = [0]
    [action_infect_node(g, n, forced=True) for n in initial_infected]

    for s in range(steps):
        g = simulate_one_step(g)
        print('\n\n\n\n\nNEW DAY\n\n\n\n')
    return g


def generate_graph(*args):
    """Selector function for which graph generator to use"""
    f = generate_barabasi
    return f(*args)


def generate_barabasi(nodes, edges) -> nx.Graph:
    """
    Generate a social-network graph to represent a given population.
    :return:
    """

    g_barabasi = nx.barabasi_albert_graph(nodes, edges)

    return g_barabasi


def generate_eerg(nodes, p) -> nx.Graph:
    """
    Generate a social-network graph to represent a given population.
    :return:
    """

    eerg = nx.erdos_renyi_graph(nodes, p)

    return eerg


def generate_Watts(nodes, knn, p) -> nx.Graph:
    """
    Generate a social-network graph to represent a given population.
    :return:
    """

    watts = nx.watts_strogatz_graph(nodes, knn, p)

    return watts


simulate(0.2, 10)
