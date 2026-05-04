from datetime import datetime
from gtfs_data import GTFSData
from dijkstra import find_route_with_dijkstra
from a_star import find_route_with_a_star
from a_star_heuristic import basic_time_heuristic
from tabu_search import tabu_search


if __name__ == "__main__":
    test_dt = datetime(2026, 3, 20, 8, 0, 0)
    start_stop_id = "1413291" # Wrocław Główny
    end_stop_id = "1413222"   # Kudowa-Zdrój
    data = GTFSData("Lista1/data")

    #find_route_with_dijkstra(data, start_stop_id, end_stop_id, test_dt, 't')
    find_route_with_dijkstra(data, start_stop_id, end_stop_id, test_dt, 'p')

    # find_route_with_a_star(data, start_stop_id, end_stop_id, test_dt, basic_time_heuristic, 't')
    # find_route_with_a_star(data, start_stop_id, end_stop_id, test_dt, advanced_transfer_heuristic, 'p')
    # find_route_with_a_star(data, start_stop_id, end_stop_id, test_dt, advanced_transfer_heuristic, 'p')

    start_id = '1413380' # Wrocław Główny
    stops_to_visit = ['1413427', '1413087', '1413417'] # Żórawina, Bolesławiec, Zgorzelec
    dt = datetime(2026, 3, 20, 8, 0, 0)
    #tabu_search(data, start_id, stops_to_visit, dt, 't', basic_time_heuristic)
    # tabu_search(data, start_id, stops_to_visit, dt, 'p', advanced_transfer_heuristic)
