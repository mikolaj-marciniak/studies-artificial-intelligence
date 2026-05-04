from gtfs_data import GTFSData
from graph import Graph
from datetime import datetime
from a_star import a_star


def find_route_with_dijkstra(data: GTFSData, start_stop_id: str, end_stop_id: str, departure_dt: datetime, criterion: str) -> None:
    start_stop_name, end_stop_name, result, computation_time, graph = dijkstra(
        data,
        start_stop_id,
        end_stop_id,
        departure_dt,
        criterion
    )

    print_dijkstra_result(start_stop_name, end_stop_name, result, computation_time, criterion, graph)

def dijkstra(data: GTFSData, start_stop_id: str, end_stop_id: str, departure_dt: datetime, criterion: str) -> tuple:
    return a_star(
        data, 
        start_stop_id, 
        end_stop_id, 
        departure_dt, 
        dijkstra_heuristic_function, 
        criterion
    )


def dijkstra_heuristic_function(graph: Graph, parent_id: str, end_parent_id: str) -> float:
    return 0.0

def format_seconds_to_hhmmss(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def print_dijkstra_result(start_stop_name: str, end_stop_name: str, result, computation_time: float, criterion: str, graph: Graph) -> None:
    print("\n" + "=" * 70)
    print("WYNIK ALGORYTMU DIJKSTRY")
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