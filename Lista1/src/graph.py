from edge import Edge
from gtfs_data import GTFSData
from datetime import datetime
import pandas as pd


class Graph:
    def __init__(self):
        self.stops = {}
        self.edges_by_parent = {}

    def add_stop(self, stop_id: str, stop_name: str, parent_station: str, lat: float, lon: float) -> None:
        if parent_station is None or parent_station == "":
            parent_station = stop_id

        self.stops[stop_id] = {
            "stop_name": stop_name,
            "parent_station": parent_station,
            "lat": lat,
            "lon": lon
        }

    def add_edge(self, edge: Edge) -> None:
        if edge.from_parent_stop_id not in self.edges_by_parent:
            self.edges_by_parent[edge.from_parent_stop_id] = []
        self.edges_by_parent[edge.from_parent_stop_id].append(edge)

    def create_graph_from_gtfs_data(self, data: GTFSData, departure_dt: datetime) -> None:
        self.stops = {}
        self.edges_by_parent = {}
        
        stops: pd.DataFrame = data.stops.copy()
        for _, row in stops.iterrows():
            self.add_stop(
                stop_id=row["stop_id"],
                stop_name = row["stop_name"],
                parent_station=row["parent_station"],
                lat = row["stop_lat"],
                lon = row["stop_lon"]
            )
        
        rides: pd.DataFrame  = data.get_rides_for_date(departure_dt)
        for _, row in rides.iterrows():
            edge = Edge(
                from_stop_id = row["from_stop_id"],
                to_stop_id = row["to_stop_id"],
                from_parent_stop_id = row["from_parent_stop_id"],
                to_parent_stop_id = row["to_parent_stop_id"],
                departure_time = row["departure_time"],
                arrival_time = row["arrival_time"],
                trip_id = row["trip_id"],
                line_name = row["line_name"]
            )
            self.add_edge(edge)