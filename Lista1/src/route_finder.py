from Lista1.src.gtfs_data import GTFSLoader
from datetime import datetime


def find_route(loader: GTFSLoader, start_stop_id: str, end_stop_id: str, criterion: str, departure_datetime: datetime, transfer_time: int) -> None:
    pass

def find_tsp_route(loader: GTFSLoader, start_stop_id: str, stops_to_visit: list[str], criterion: str, departure_date: str, departure_time: str, transfer_time: int):
    pass