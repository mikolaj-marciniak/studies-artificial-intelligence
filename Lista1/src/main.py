from gtfs_data import GTFSData
from graph import Graph
from datetime import datetime


if __name__ == "__main__":
    data = GTFSData("Lista1/data")
    graph = Graph()
    graph.create_graph_from_gtfs_data(data, datetime.now())
    for edge in graph.edges_by_parent[1413380]:
        print(edge.departure_time, edge.trip_id, edge.line_name, edge.from_stop_id, edge.to_stop_id, edge.from_parent_stop_id)