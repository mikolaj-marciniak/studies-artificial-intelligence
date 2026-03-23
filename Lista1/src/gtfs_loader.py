from pathlib import Path
import pandas as pd


AGENCY_FILE = "agency.txt"
ROUTES_FILE = "routes.txt"
STOPS_FILE = "stops.txt"
TRIPS_FILE = "trips.txt"
STOP_TIMES_FILE = "stop_times.txt"
CALENDAR_FILE = "calendar.txt"
CALENDAR_DATES_FILE = "calendar_dates.txt"
FEED_INFO_FILE = "feed_info.txt"


class GTFSLoader:
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