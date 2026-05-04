from typing import Callable
from math import inf
from datetime import datetime
from graph import Graph
from gtfs_data import GTFSData
import heapq
import time


def format_seconds_to_hhmmss(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def find_route_with_a_star(data: GTFSData, start_stop_id: str, end_stop_id: str, departure_dt: datetime, heuristic_function: Callable[[Graph, str, str], float], criterion: str) -> None:
    start_stop_name, end_stop_name, result, computation_time, graph = a_star(data, start_stop_id, end_stop_id, departure_dt, heuristic_function, criterion)

    print_a_star_result(start_stop_name, end_stop_name, result, computation_time, criterion, graph)


def a_star(data: GTFSData, start_stop_id: str, end_stop_id: str, departure_dt: datetime, heuristic_function: Callable[[Graph, str, str], float], criterion: str) -> tuple:
    graph = Graph()
    graph.create_graph_from_gtfs_data(data, departure_dt)
    if criterion == 't':
        result = a_star_by_time(graph, start_stop_id, end_stop_id, departure_dt, heuristic_function)
    elif criterion == 'p':
        result = a_star_by_transfer(graph, start_stop_id, end_stop_id, departure_dt, heuristic_function)
    else:
        raise ValueError("Niepoprawne kryterium. Użyj 't' dla czasu albo 'p' dla przesiadek.")
    return result

def a_star_by_time(graph: Graph, start_stop_id: str, end_stop_id: str, departure_dt: datetime, heuristic_function: Callable[[Graph, str, str], float]) -> tuple:
    start_time_measure = time.perf_counter()

    start_parent = graph.stops[start_stop_id]["parent_station"]
    end_parent = graph.stops[end_stop_id]["parent_station"]

    start_stop_name = graph.stops[start_stop_id]["stop_name"]
    end_stop_name = graph.stops[end_stop_id]["stop_name"]

    start_time_sec = (
        departure_dt.hour * 3600
        + departure_dt.minute * 60
        + departure_dt.second
    )

    g_score = {start_parent: start_time_sec}
    prev_edge = {}

    start_h = heuristic_function(graph, start_parent, end_parent)
    priority_queue = [(start_time_sec + start_h, start_time_sec, start_parent)]

    while priority_queue:
        _, current_time, current_parent = heapq.heappop(priority_queue)

        if current_time > g_score.get(current_parent, inf):
            continue

        if current_parent == end_parent:
            break

        for edge in graph.edges_by_parent.get(current_parent, []):
            departure_sec = edge.departure_time_in_seconds
            arrival_sec = edge.arrival_time_in_seconds

            if departure_sec < current_time:
                continue

            next_parent = edge.to_parent_stop_id
            new_g = arrival_sec

            if new_g < g_score.get(next_parent, inf):
                g_score[next_parent] = new_g
                prev_edge[next_parent] = edge

                h = heuristic_function(graph, next_parent, end_parent)
                new_f = new_g + h
                heapq.heappush(priority_queue, (new_f, new_g, next_parent))

    end_time_measure = time.perf_counter()
    computation_time = end_time_measure - start_time_measure

    if end_parent not in g_score:
        return (start_stop_name, end_stop_name, None, computation_time, graph)

    path = []
    current_parent = end_parent

    while current_parent != start_parent:
        edge = prev_edge[current_parent]
        path.append(edge)
        current_parent = edge.from_parent_stop_id

    path.reverse()

    arrival_time_sec = g_score[end_parent]
    total_travel_time_sec = arrival_time_sec - start_time_sec

    transfers_count = 0
    previous_trip_id = None

    for edge in path:
        if previous_trip_id is None:
            previous_trip_id = edge.trip_id
        elif edge.trip_id != previous_trip_id:
            transfers_count += 1
            previous_trip_id = edge.trip_id

    result = {
        "path": path,
        "arrival_time": path[-1].arrival_time if path else departure_dt.strftime("%H:%M:%S"),
        "total_travel_time_seconds": total_travel_time_sec,
        "transfers_count": transfers_count,
    }

    return (start_stop_name, end_stop_name, result, computation_time, graph)

def a_star_by_transfer(graph: Graph, start_stop_id: str, end_stop_id: str, departure_dt: datetime, heuristic_function: Callable[[Graph, str, str], float]) -> tuple:
    start_time_measure = time.perf_counter()

    start_parent = graph.stops[start_stop_id]["parent_station"]
    end_parent = graph.stops[end_stop_id]["parent_station"]

    start_stop_name = graph.stops[start_stop_id]["stop_name"]
    end_stop_name = graph.stops[end_stop_id]["stop_name"]

    start_time_sec = (
        departure_dt.hour * 3600
        + departure_dt.minute * 60
        + departure_dt.second
    )

    start_state = (start_parent, None)
    g_score = {start_state: 0}
    arrival_time_at_state = {start_state: start_time_sec}
    prev_state = {}
    prev_edge = {}

    start_h = heuristic_function(graph, start_parent, end_parent)
    priority_queue = [(start_h, 0, start_time_sec, start_parent, None)]

    best_end_state = None

    while priority_queue:
        _, current_transfers, current_time, current_parent, current_trip_id = heapq.heappop(priority_queue)
        current_state = (current_parent, current_trip_id)

        best_known_transfers = g_score.get(current_state, inf)
        best_known_time = arrival_time_at_state.get(current_state, inf)

        if current_transfers > best_known_transfers:
            continue
        if current_transfers == best_known_transfers and current_time > best_known_time:
            continue

        if current_parent == end_parent:
            best_end_state = current_state
            break

        for edge in graph.edges_by_parent.get(current_parent, []):
            departure_sec = edge.departure_time_in_seconds
            arrival_sec = edge.arrival_time_in_seconds

            if departure_sec < current_time:
                continue

            next_parent = edge.to_parent_stop_id
            next_trip_id = edge.trip_id

            if current_trip_id is None:
                transfer_cost = 0
            elif current_trip_id == next_trip_id:
                transfer_cost = 0
            else:
                transfer_cost = 1

            new_transfers = current_transfers + transfer_cost
            next_state = (next_parent, next_trip_id)
            new_arrival_time = arrival_sec

            old_transfers = g_score.get(next_state, inf)
            old_arrival_time = arrival_time_at_state.get(next_state, inf)

            is_better = (
                new_transfers < old_transfers
                or (new_transfers == old_transfers and new_arrival_time < old_arrival_time)
            )

            if is_better:
                g_score[next_state] = new_transfers
                arrival_time_at_state[next_state] = new_arrival_time
                prev_state[next_state] = current_state
                prev_edge[next_state] = edge

                h = heuristic_function(graph, next_parent, end_parent)
                new_f = new_transfers + h

                heapq.heappush(
                    priority_queue,
                    (new_f, new_transfers, new_arrival_time, next_parent, next_trip_id)
                )

    end_time_measure = time.perf_counter()
    computation_time = end_time_measure - start_time_measure

    if best_end_state is None:
        return (start_stop_name, end_stop_name, None, computation_time, graph)

    path = []
    current_state = best_end_state

    while current_state != start_state:
        edge = prev_edge[current_state]
        path.append(edge)
        current_state = prev_state[current_state]

    path.reverse()

    arrival_time_sec = arrival_time_at_state[best_end_state]
    total_travel_time_sec = arrival_time_sec - start_time_sec
    transfers_count = g_score[best_end_state]

    result = {
        "path": path,
        "arrival_time": path[-1].arrival_time if path else departure_dt.strftime("%H:%M:%S"),
        "total_travel_time_seconds": total_travel_time_sec,
        "transfers_count": transfers_count,
    }

    return (start_stop_name, end_stop_name, result, computation_time, graph)

def print_a_star_result(start_stop_name: str, end_stop_name: str, result, computation_time: float, criterion: str, graph: Graph) -> None:
    print("\n" + "=" * 70)
    print("WYNIK ALGORYTMU A*")
    print("=" * 70)
    print(f"Start: {start_stop_name}")
    print(f"Cel:   {end_stop_name}")
    print(f"Kryterium: {'czas' if criterion == 't' else 'liczba przesiadek'}")
    print(f"Czas obliczeń: {computation_time:.6f} s")

    if result is None:
        print("\nNie znaleziono trasy.")
        print("=" * 70)
        return

    print("\n--- PODSUMOWANIE ---")
    print(f"Godzina przyjazdu: {result['arrival_time']}")
    print(f"Liczba przesiadek: {result['transfers_count']}")

    if "total_travel_time_seconds" in result:
        print(f"Łączny czas podróży: {format_seconds_to_hhmmss(result['total_travel_time_seconds'])}")

    path = result["path"]

    if not path:
        print("\nStart i cel znajdują się w tym samym miejscu.")
        print("=" * 70)
        return

    print("\n--- SZCZEGÓŁY TRASY ---")

    for i, edge in enumerate(path, start=1):
        print(
            f"{i:02d}. "
            f"{graph.stops[edge.from_stop_id]['stop_name']} {graph.stops[edge.from_stop_id]['platform_code']} ({edge.departure_time}) -> "
            f"{graph.stops[edge.to_stop_id]['stop_name']} {graph.stops[edge.to_stop_id]['platform_code']} ({edge.arrival_time}) "
            f"| linia: {edge.line_name}"
        )

    print("=" * 70)