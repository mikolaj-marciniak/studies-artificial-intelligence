from graph import Graph
from math import sqrt


def get_distance_between_points(graph: Graph, current_parent_id: str, end_parent_id: str) -> float:
    current_stop = graph.stops[current_parent_id]
    end_stop = graph.stops[end_parent_id]

    x1 = float(current_stop["lon"])
    y1 = float(current_stop["lat"])
    x2 = float(end_stop["lon"])
    y2 = float(end_stop["lat"])

    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * 111000

def basic_time_heuristic(graph: Graph, current_parent_id: str, end_parent_id: str) -> float:
    if current_parent_id == end_parent_id:
        return 0.0

    distance = get_distance_between_points(graph, current_parent_id, end_parent_id)
    average_speed_m_per_s = 60.0

    estimated_time_sec = distance / average_speed_m_per_s
    return estimated_time_sec

def get_lines_for_parent(graph: Graph, parent_id: str) -> set[str]:
    edges = graph.edges_by_parent.get(parent_id, [])
    lines = set()

    for edge in edges:
        line = edge.line_name
        lines.add(line)

    return lines

def get_lines_to_parent(graph: Graph, parent_id: str) -> set[str]:
    result = set()
    for edge_list in graph.edges_by_parent.values():
        for edge in edge_list:
            if edge.to_parent_stop_id == parent_id:
                result.add(edge.line_name)

    return result

def basic_transfer_heuristic(graph: Graph, current_parent_id: str, end_parent_id: str) -> float:
    if current_parent_id == end_parent_id:
        return 0.0

    current_lines = get_lines_for_parent(graph, current_parent_id)
    end_lines = get_lines_for_parent(graph, end_parent_id)

    if current_lines & end_lines:
        return 0.0

    return 1.0