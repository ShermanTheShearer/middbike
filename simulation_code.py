from __future__ import annotations
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple
from request import Request

def build_complete_digraph(travel_time: np.ndarray) -> nx.DiGraph:
    """
    Build a complete digraph whose edge attribute 'time' holds one-way travel
    time in minutes. 
    ----------------
    Parameters:
    travel_time - [i, j] represents the travel time in mins from i to j

    Returns:
    G - complete digraph G populated based on data provided
    """
    n = travel_time.shape[0] # should be 10, since the matrix [10, 10][0] = 10
    G = nx.complete_graph(n, create_using = nx.DiGraph)
    for u, v in G.edges: # for edge uv, the label time = travel_time[u, v]
        G.edges[u, v]["time"] = int(travel_time[u, v])
    return G

def simulation(
        G: nx.DiGraph,
        distribution: Dict[int, np.ndarray],
        possibilities: Dict[int, List[float]],
        *,
        T: int,
        max_bikes_per_hub: int = 10,
        initial_bikes_per_hub: int = 5,
        rng: np.random.Generator | None = None,
) -> Tuple[np.ndarray, np.ndarray, List[Request]]:
    """
    Parameters:
    G - K_10 generated from data
    distribution - 24-element np.ndarray hourly rental requests at each hub
    possibilities - 10-element destination probabilities for each hub, [origin][origin] must be 0.0
    keyword args - must be passed with name
        max_bikes_per_hub - 10
        initial_bikes_per_hub - 5 for simplicity 
        rng - NumPy generator for reproducibility

    Returns:
    no_bike_events - 24-element np.ndarray representing the no. of no-bike events every hour in the system
    no_parking_events - 24-element np.ndarray representing the no. of no-space events every hour in the system

    """
    
    # initialize NumPy random number generator
    if rng is None:
        rng = np.random.default_rng()

    num_hubs = G.number_of_nodes()

    # pre-build request objects
    req_pool: Dict[int, List[Request]] = {}
    all_requests: List[Request] = []
    for hub in range(num_hubs):
        n_req = int(distribution[hub].sum())
        bag = [Request() for _ in range(n_req)]
        req_pool[hub] = bag
        all_requests.extend(bag)
    
    bike_stock = np.full(num_hubs, initial_bikes_per_hub, dtype = int) # 10-element array, no. of bikes at each hub
    
    # trips currently on the road, each element (minutes_remaining, destination_hub)
    in_transit: List[Request] = []

    no_bike_events = np.zeros(T, dtype = int) # sum of no-bike events, each hour of the day
    no_parking_events = np.zeros(T, dtype = int) # sum of no-parking events, each hour of the day

    for hour in range(T):

        # for simplicity, advance all in-transit bikes by 60 mins
        # dock whose remaining time has hit zero or below
        # on_road: array of requests still riding after the current hour is processed
        on_road: List[Request] = []
        
        for req in in_transit:
            req.minutes_left -= 60

            if req.minutes_left > 0:
                on_road.append(req)
                continue

            dest = req.dest
            
            # attempt to dock a bike at dest
            if bike_stock[dest] < max_bikes_per_hub:
                bike_stock[dest] += 1
                continue
                
            no_parking_events[hour] += 1

            candidate = None
            for offset in range(1, num_hubs):
                for new_hub in (dest - offset, dest + offset):
                    if 0 <= new_hub < num_hubs:
                        candidate = new_hub
                        break
                if candidate is not None:
                    break
            
            if candidate is None:
                req.minutes_left = 60
                on_road.append(req)
                continue

            extra_time = int(G.edges[dest, candidate]["time"])
            req.dest = candidate
            req.minutes_left = extra_time
            on_road.append(req)
                    
        in_transit = on_road

        # process rental requests that occur during this hour
        for hub in range(num_hubs):
            for _ in range(int(distribution[hub][hour])):
                req = req_pool[hub].pop() if req_pool[hub] else Request()
                all_requests.append(req)
                req.origin = hub

                # attempt to rent at hub
                if bike_stock[hub] == 0: # if no bike left
                    no_bike_events[hour] += 1
                    req.success = False
                    continue

                # successful checkout
                bike_stock[hub] -= 1
                dest = rng.choice(num_hubs, p=possibilities[hub]) # assign destination based on probability array
                req.dest = dest
                #trip duration from edge attribute in G
                req.minutes_left = int(G.edges[hub, dest]["time"])
                req.success = True
                in_transit.append(req)
    

    return no_bike_events, no_parking_events, all_requests

    
