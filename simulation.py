from icecream import ic
from mkl_random.mklrand import choice, uniform
from numpy.random.mtrand import sample
import matplotlib.pyplot as plt
from utils import *
from constants import *
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time


def initialize_graph(g, susceptible=True, exposed=False, infectious=False, recovered=False):
    p = {
        'alive'            : True,
        'susceptible'      : susceptible,
        'exposed'          : exposed,
        'infectious'       : infectious,
        'recovered'        : recovered,
        'days_exposed'     : 0,
        'prob_transmission': 0
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
    (g.nodes[n])['prob_transmission'] = 0
    (g.nodes[n])['susceptible'] = False


def action_kill_node(g, n):
    """Logic to kill a node which does not survive covid after active duration"""
    assert g.nodes[n]['alive']
    # death logic
    (g.nodes[n])['alive'] = False
    (g.nodes[n])['infectious'] = False
    (g.nodes[n])['exposed'] = False
    (g.nodes[n])['days_exposed'] = -inf
    (g.nodes[n])['prob_transmission'] = 0
    (g.nodes[n])['susceptible'] = False


def action_infect_node(g, n, p, forced=False):
    """Logic to infect a node, generally called by neighbors. Will infect with CHANCE_TRANSMISSION_INFECTED."""
    if not g.nodes[n]['alive']:
        # ignore nodes that have built an immunity
        return

    if g.nodes[n]['recovered']:
        return

    if not g.nodes[n]['exposed']:
        if forced or ((not forced) and uniform() < p):
            (g.nodes[n])['exposed'] = True
            (g.nodes[n])['susceptible'] = False
            (g.nodes[n])['days_exposed'] = -1
            (g.nodes[n])['prob_transmission'] = CHANCE_TRANSMISSION_EXPOSED


def process_exposed_nodes(g, n):
    """Logic to process exposed nodes and make them infectious"""
    if g.nodes[n]['exposed']:
        if not g.nodes[n]['infectious'] and g.nodes[n]['days_exposed'] > INCUBATION_PERIOD:
            (g.nodes[n])['infectious'] = True
            (g.nodes[n])['prob_transmission'] = CHANCE_TRANSMISSION_INFECTED


def process_terminal_node(g, n):
    """Logic to process terminal nodes, aka those at the end of the active disease period"""

    if not g.nodes[n]['alive'] or g.nodes[n]['recovered']:
        return

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
            [action_infect_node(g, x, node['prob_transmission']) for x in g.neighbors(n) if
             uniform() < prob_interaction(x, node)]

    return g


def disg(g):
    for n in g.nodes:
        print(g.nodes[n], n)


def debug_info(g, s, verbose=False):
    params = {
        'exposed'    : 0,
        'alive'      : 0,
        'infectious' : 0,
        'recovered'  : 0,
        'susceptible': 0,
        }

    for n in g.nodes:
        for p in params.keys():
            if g.nodes[n][p]:
                params[p] += 1

    if verbose:
        ic('***debug %s ***' % s)
        ic(params)
    return params


def simulate(r0, N=1000, steps=100):
    """Driver function to run a simulation for a given number of days with given input parameters"""
    g = generate_graph(N, 5)
    # g = generate_Watts(100000, 4, 0.01)
    # initialize the graph
    initialize_graph(g)

    N = len(g.nodes)
    initial_infected = choice(list(range(N)), int(r0 * N))
    if len(initial_infected) == 0:
        initial_infected = [0]
    [action_infect_node(g, n, 1, forced=True) for n in initial_infected]

    history = []
    for s in range(steps):
        g = simulate_one_step(g)
        p = debug_info(g, s, verbose=True)
        history.append(p)

    return g, history

def simulate_graph(r0, N, steps=100):
    """Driver function to draw a simulation for a given number of days with given input parameters"""
    g = generate_graph(N, 5)
    # g = generate_Watts(100000, 4, 0.01)
    # initialize the graph
    initialize_graph(g)

    N = len(g.nodes)
    initial_infected = choice(list(range(N)), int(r0 * N))
    if len(initial_infected) == 0:
        initial_infected = [0]
    [action_infect_node(g, n, 1, forced=True) for n in initial_infected]

    color_map = ['green']*len(g.nodes)
    pos = nx.spring_layout(g)
    nx.draw(g, pos, node_color=color_map, with_labels=False)
    for s in range(steps):
        g = simulate_one_step(g)
        color_map = []
        for n in g.nodes:
            color_n = ''
            if g.nodes[n]['alive']:
                color_n = 'green'
            else:
                color_n = 'black'
            if g.nodes[n]['exposed']:
                color_n = 'yellow'
            if g.nodes[n]['infectious']:
                color_n = 'red'
            if g.nodes[n]['recovered']:
                color_n = 'blue'
            color_map.append(color_n)
        nx.draw(g, pos, node_color=color_map, with_labels=False)
        time.sleep(1)
        plt.show()
        # disg(g)
        # print('\n\n\n\n\nNEW DAY\n\n\n\n')
        # debug_info(g, s)
    return g

def graph_debug(g, history):
    # make graphs

    tp = {}

    for x in history[0].keys():
        tp[x] = []

    for h in history:
        for k, v in h.items():
            tp[k].append(v)

    x = list(range(len(history)))
    for k, v in tp.items():
        plt.plot(x, v, label=str(k))
    plt.legend()
    plt.show()

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


# r = simulate(0.0005, 100000, steps=75 )
# graph_debug(*r)

simulate_graph(0.0005, 100000, steps=75 )