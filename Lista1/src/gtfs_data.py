from pathlib import Path
import pandas as pd
from datetime import datetime


AGENCY_FILE = "agency.txt"
ROUTES_FILE = "routes.txt"
STOPS_FILE = "stops.txt"
TRIPS_FILE = "trips.txt"
STOP_TIMES_FILE = "stop_times.txt"
CALENDAR_FILE = "calendar.txt"
CALENDAR_DATES_FILE = "calendar_dates.txt"
FEED_INFO_FILE = "feed_info.txt"


class GTFSData:
    def __init__(self, path: str | Path) -> None:
        self.path: Path = Path(path)

        self.agency: pd.DataFrame | None = None
        self.routes: pd.DataFrame | None = None
        self.stops: pd.DataFrame | None = None
        self.trips: pd.DataFrame | None = None
        self.stop_times: pd.DataFrame | None = None
        self.calendar: pd.DataFrame | None = None
        self.calendar_dates: pd.DataFrame | None = None
        self.feed_info: pd.DataFrame | None = None

        self.load_all()

    def load_all(self) -> None:
        self.agency = self._load_csv(AGENCY_FILE)
        self.routes = self._load_csv(ROUTES_FILE)
        self.stops = self._load_csv(STOPS_FILE)
        self.trips = self._load_csv(TRIPS_FILE)
        self.stop_times = self._load_csv(STOP_TIMES_FILE)
        self.calendar = self._load_csv(CALENDAR_FILE)
        self.calendar_dates = self._load_csv(CALENDAR_DATES_FILE)
        self.feed_info = self._load_csv(FEED_INFO_FILE)

    def _load_csv(self, file_name: str | Path) -> pd.DataFrame:
        file_path = self.path / file_name

        if not file_path.exists():
            raise FileNotFoundError(f"Brakuje pliku: {file_path}")
        
        return pd.read_csv(file_path, encoding="utf-8")
    
    def get_service_ids_for_date(self, dt: datetime) -> set[str]:
        date = dt.strftime("%Y%m%d")
        day = dt.strftime("%A").lower()

        calendar = self.calendar.copy()
        calendar_dates = self.calendar_dates.copy()

        calendar["start_date"] = calendar["start_date"].astype(str)
        calendar["end_date"] = calendar["end_date"].astype(str)

        calendar_dates["date"] = calendar_dates["date"].astype(str)

        active_service_ids = set(
            calendar[
                (calendar["start_date"] <= date) &
                (calendar["end_date"] >= date) &
                (calendar[day] == 1)
            ]["service_id"]
        )

        good_exceptions = set(
            calendar_dates[
                (calendar_dates["date"] == date) &
                (calendar_dates["exception_type"] == 1)
            ]["service_id"]
        )

        bad_exceptions = set(
            calendar_dates[
                (calendar_dates["date"] == date) &
                (calendar_dates["exception_type"] == 2)
            ]["service_id"]
        )

        active_service_ids.update(good_exceptions)
        active_service_ids.difference_update(bad_exceptions)

        return active_service_ids
    
    def get_trips_ids_for_date(self, dt: datetime) -> pd.DataFrame:
        service_ids = self.get_service_ids_for_date(dt)
        trips = self.trips.copy()
        return trips[trips["service_id"].isin(service_ids)]["trip_id"]
    
    def get_stop_times_for_date(self, dt: datetime) -> pd.DataFrame:
        trip_ids = self.get_trips_ids_for_date(dt)

        stop_times = self.stop_times.copy()

        stop_times = stop_times[stop_times["trip_id"].isin(trip_ids)]

        stop_times = stop_times.sort_values(by=["trip_id", "stop_sequence"])

        return stop_times
    
    def get_rides_for_date(self, dt: datetime) -> pd.DataFrame:
        stop_times = self.get_stop_times_for_date(dt).copy()

        rides = stop_times.copy()

        rides["next_trip_id"] = rides["trip_id"].shift(-1)

        rides["from_stop_id"] = rides["stop_id"]
        rides["to_stop_id"] = rides["stop_id"].shift(-1)

        stops = self.stops[["stop_id", "parent_station"]].copy()
        stops = stops.rename(columns={
            "stop_id": "from_stop_id",
            "parent_station": "from_parent_stop_id"
        })

        rides = rides.merge(stops, on="from_stop_id", how="left")
        rides["from_parent_stop_id"] = rides["from_parent_stop_id"].fillna(rides["from_stop_id"])
        
        stops = stops.rename(columns={
            "from_stop_id": "to_stop_id",
            "from_parent_stop_id": "to_parent_stop_id"
        })

        rides = rides.merge(stops, on="to_stop_id", how="left")
        rides["to_parent_stop_id"] = rides["to_parent_stop_id"].fillna(rides["to_stop_id"])

        rides["arrival_time"] = rides["arrival_time"].shift(-1)
        
        trips = self.trips[["trip_id", "route_id"]].copy()
        rides = rides.merge(trips, on="trip_id", how="left")

        routes = self.routes[["route_id", "route_short_name", "route_long_name"]].copy()
        routes["line_name"] = routes["route_short_name"].fillna("")
        routes.loc[routes["line_name"] == "", "line_name"] = routes["route_long_name"]

        rides = rides.merge(routes, on="route_id", how="left")

        rides = rides[rides["trip_id"] == rides["next_trip_id"]].copy()

        return rides[[
            "from_stop_id",
            "to_stop_id",
            "from_parent_stop_id",
            "to_parent_stop_id",
            "departure_time",
            "arrival_time",
            "trip_id",
            "line_name"
        ]]