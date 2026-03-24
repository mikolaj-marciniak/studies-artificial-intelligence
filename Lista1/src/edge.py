class Edge:
    def __init__(self, from_stop_id: str, to_stop_id: str, from_parent_stop_id: str, to_parent_stop_id: str, departure_time: str, arrival_time: str, trip_id: str, line_name: str):
        self.from_stop_id: str = from_stop_id
        self.to_stop_id: str = to_stop_id

        self.from_parent_stop_id: str = from_parent_stop_id
        self.to_parent_stop_id: str = to_parent_stop_id

        self.departure_time: str = departure_time
        self.arrival_time: str = arrival_time

        self.departure_time_in_seconds: int = self._calculate_to_seconds(departure_time)
        self.arrival_time_in_seconds: int = self._calculate_to_seconds(arrival_time)

        self.trip_id: str = trip_id
        self.line_name: str = line_name

    def _calculate_to_seconds(self, time: str) -> int:
        hours, minutes, seconds = map(int, time.split(":"))
        return hours * 3600 + minutes * 60 + seconds