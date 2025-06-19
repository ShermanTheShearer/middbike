import numpy as np
import networkx as nx
from typing import List

#bike hubs around Middlebury College and town
location_index = {
    "twilight": 0,
    "athletic_complex": 1,
    "student_center": 2,
    "kinney_drugs": 3,
    "food_coop": 4,
    "hannaford": 5,
    "porter_hospital": 6,
    "amtrak_station": 7,
    "bihall": 8,
    "bus_stop": 9
}

index_location = {v: k for k, v in location_index.items()}

matrix = [[0, 11, 11, 6, 6, 13, 6, 10, 8, 7],
    [7, 0, 6, 4, 8, 9, 5, 6, 3, 4],
    [11, 7, 0, 5, 10, 12, 7, 9, 4, 4],
    [5, 5, 5, 0, 6, 9, 3, 6, 3, 1],
    [4, 11, 11, 5, 0, 7, 4, 10, 8, 6],
    [11, 11, 13, 10, 8, 0, 8, 7, 10, 10],
    [5, 8, 9, 3, 4, 5, 0, 8, 6, 4],
    [8, 6, 9, 5, 9, 7, 6, 0, 6, 6],
    [6, 5, 3, 2, 7, 9, 4, 5, 0, 1],
    [5, 5, 5, 1, 6, 9, 3, 6, 2, 0]]

"""
Creates graph with each node being a bike hub in Middlebury and each edge being the distance it takes to get from nodes k to v
param: matrix with each index representing the time it takes to get from x hub to y hub
returns: map of Middlebury with hubs as nodes and edges as bike time between nodes (minutes)
"""
def create_graph(matrix: List[List[int]]) -> nx.DiGraph:
    num_hubs = len(matrix)
    graph = nx.DiGraph()
    for i in range(num_hubs):
        graph.add_node(index_location[i])
    for i in range(num_hubs):
        for j in range(num_hubs):
            if i != j:
                from_hub = index_location[i]
                to_hub = index_location[j]
                graph.add_edge(from_hub, to_hub, time=matrix[i][j]) 
    return graph
