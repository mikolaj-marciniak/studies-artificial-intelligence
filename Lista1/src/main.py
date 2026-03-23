from gtfs_loader import GTFSLoader


if __name__ == "__main__":
    loader = GTFSLoader("Lista1/data")
    loader.load_all()
    print(loader.agency.head())