from gtfs_data import GTFSData
from datetime import datetime, timedelta
from typing import Callable
from graph import Graph
from a_star import a_star
import random
import time


def generate_neighbors(order: list[str]):
    neighbors = []

    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            new_order = order.copy()
            new_order[i], new_order[j] = new_order[j], new_order[i]

            move = (i, j)
            neighbors.append((new_order, move))

    return neighbors

def build_full_order(start_stop_id: str, visit_order: list[str]) -> list[str]:
    return [start_stop_id] + visit_order + [start_stop_id]

def evaluate_solution(data: GTFSData, start_stop_id: str, visit_order: list[str], departure_dt: datetime, heuristic_function: Callable[[Graph, str, str], float], criterion: str):
    full_order = build_full_order(start_stop_id, visit_order)

    current_departure_dt = departure_dt
    total_cost = 0
    all_segments = []

    second_cost = 0
    transfer_cost = 0

    last_trip_id = None

    for i in range(len(full_order) - 1):
        from_stop_id = full_order[i]
        to_stop_id = full_order[i + 1]

        start_name, end_name, result, computation_time, graph = a_star(data, from_stop_id, to_stop_id,current_departure_dt, heuristic_function, criterion)

        if result is None or not result["path"]:
            return None

        all_segments.append((from_stop_id, to_stop_id, result))

        second_cost += result["total_travel_time_seconds"]
        transfer_cost += result["transfers_count"]

        if last_trip_id is not None and last_trip_id != result["path"][0].trip_id:
            transfer_cost += 1

        last_trip_id = result["path"][-1].trip_id

        if criterion == 't':
            total_cost = second_cost
        else:
            total_cost = transfer_cost

        current_departure_dt = current_departure_dt + timedelta(seconds=result["total_travel_time_seconds"])

    return {"cost": total_cost, "segments": all_segments, "second_cost": second_cost, "transfer_cost": transfer_cost}

def format_seconds_to_hhmmss(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def print_tabu_search_result(start_stop_id: str, visit_order: list[str], evaluation, computation_time: float, criterion: str, graph: Graph, departure_dt: datetime) -> None:
    print("\n" + "=" * 70)
    print("WYNIK ALGORYTMU TABU SEARCH")
    print("=" * 70)
    print(f"Start: {graph.stops[start_stop_id]['stop_name']}")
    print(f"Kryterium: {'czas' if criterion == 't' else 'liczba przesiadek'}")
    print(f"Czas obliczeń: {computation_time:.6f} s")

    if evaluation is None:
        print("\nTABU SEARCH: nie znaleziono rozwiązania.")
        print("=" * 70)
        return

    print("\n--- PODSUMOWANIE ---")

    route_names = [graph.stops[start_stop_id]["stop_name"]]
    for stop_id in visit_order:
        route_names.append(graph.stops[stop_id]["stop_name"])
    route_names.append(graph.stops[start_stop_id]["stop_name"])

    total_transfers = 0
    total_time = 0

    for _, _, result in evaluation["segments"]:
        total_transfers += result["transfers_count"]
        total_time += result["total_travel_time_seconds"]

    last_segment_result = evaluation["segments"][-1][2]

    print("Kolejność odwiedzania:")
    print(" -> ".join(route_names))

    print(f"Godzina wyjazdu: {departure_dt.strftime('%H:%M:%S')}")
    print(f"Liczba przesiadek: {evaluation['transfer_cost']}")
    print(f"Godzina dotarcia do celu: {last_segment_result['arrival_time']}")

    if criterion == 't':
        print(f"Łączny koszt: {evaluation['cost']}")
        print(f"Łączny czas podróży: {format_seconds_to_hhmmss(total_time)}")
    else:
        print(f"Łączny koszt: {evaluation['cost']}")
        print(f"Łączny czas podróży: {format_seconds_to_hhmmss(total_time)}")

    print("\n--- SZCZEGÓŁY TRASY ---")

    segment_number = 1
    for from_stop_id, to_stop_id, result in evaluation["segments"]:
        from_name = graph.stops[from_stop_id]["stop_name"]
        to_name = graph.stops[to_stop_id]["stop_name"]

        print(f"\nOdcinek: {from_name} -> {to_name}")

        path = result["path"]

        if not path:
            print("Brak przejazdów dla tego odcinka.")
            continue

        for edge in path:
            print(
                f"{segment_number:02d}. "
                f"{graph.stops[edge.from_stop_id]['stop_name']} "
                f"{graph.stops[edge.from_stop_id]['platform_code']} ({edge.departure_time}) -> "
                f"{graph.stops[edge.to_stop_id]['stop_name']} "
                f"{graph.stops[edge.to_stop_id]['platform_code']} ({edge.arrival_time}) "
                f"| linia: {edge.line_name}"
            )
            segment_number += 1

    print("=" * 70)


def tabu_search(data: GTFSData, start_stop_id: str, stops_to_visit: list[str], departure_dt: datetime, criterion: str, heuristic_function: Callable[[Graph, str, str], float]) -> None:
    start_time = time.perf_counter()

    current_solution = stops_to_visit.copy()

    current_evaluation = evaluate_solution(data, start_stop_id, current_solution, departure_dt,heuristic_function, criterion=criterion)

    best_solution = current_solution.copy()
    best_evaluation = current_evaluation

    tabu_list = []
    max_iterations = 20
    L = len(stops_to_visit)
    tabu_size = max(2, L // 2)
    iterations_without_improvement = 0

    for _ in range(max_iterations):
        neighbors = generate_neighbors(current_solution)

        sample_size = max(2, len(neighbors) // 2)
        neighbors = random.sample(neighbors, sample_size)

        best_candidate_solution = None
        best_candidate_evaluation = None
        best_candidate_move = None

        for neighbor_solution, move in neighbors:

            neighbor_evaluation = evaluate_solution(data, start_stop_id, neighbor_solution, departure_dt, heuristic_function, criterion)

            if neighbor_evaluation is None:
                continue

            is_tabu = move in tabu_list
            aspiration = best_evaluation is not None and neighbor_evaluation["cost"] < best_evaluation["cost"]

            if is_tabu and not aspiration:
                continue

            if (best_candidate_evaluation is None or neighbor_evaluation["cost"] < best_candidate_evaluation["cost"]):
                best_candidate_solution = neighbor_solution
                best_candidate_evaluation = neighbor_evaluation
                best_candidate_move = move

        if best_candidate_solution is None:
            break

        current_solution = best_candidate_solution
        current_evaluation = best_candidate_evaluation
        tabu_list.append(best_candidate_move)
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0)

        if best_evaluation is None:
            best_solution = current_solution.copy()
            best_evaluation = current_evaluation
            iterations_without_improvement = 0

        elif current_evaluation["cost"] < best_evaluation["cost"]:
            best_solution = current_solution.copy()
            best_evaluation = current_evaluation
            iterations_without_improvement = 0
            tabu_size = max(2, tabu_size - 1)

        else:
            iterations_without_improvement += 1

            if iterations_without_improvement >= 3:
                tabu_size = tabu_size + 1
                iterations_without_improvement = 0

    if best_evaluation is None:
        print("TABU SEARCH: nie znaleziono rozwiązania.")
        return

    graph = Graph()
    graph.create_graph_from_gtfs_data(data, departure_dt)
    computation_time = time.perf_counter() - start_time

    print_tabu_search_result(start_stop_id, best_solution, best_evaluation, computation_time, criterion,graph=graph, departure_dt=departure_dt)