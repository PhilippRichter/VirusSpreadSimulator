import pandas as pd
import logging
from typing import List, TextIO
import importlib.resources as pkg_resources
import data  # relative-import the *package* containing the data


def main() -> None:
    logger = logging.getLogger(__name__)

    # download airport info data
    airport_col = [
        'ID', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Lat', 'Long', 'Alt',
        'Timezone', 'DST', 'Tz database time zone', 'type', 'source'
    ]  # type: List[str]
    airports_path = pkg_resources.open_text(data, 'airports.dat')  # type: TextIO
    airport_df = pd.read_csv(airports_path, names=airport_col,
                             index_col=0)  # type: pd.DataFrame
    logger.info('Loaded airports.dat')

    # download flight routes data
    route_cols = [
        'Airline', 'Airline ID', 'Source Airport', 'Source Airport ID',
        'Dest Airport', 'Dest Airport ID', 'Codeshare', 'Stops', 'equipment'
    ]  # type: List[str]
    flights_path = pkg_resources.open_text(data, 'routes.dat')  # type: TextIO
    routes_df = pd.read_csv(flights_path,
                            names=route_cols)  # type: pd.DataFrame
    logger.info('Loaded routes.dat')

    # clean up data, change 'object' type to numeric and drop NaNs
    routes_df['Source Airport ID'] = pd.to_numeric(
        routes_df['Source Airport ID'].astype(str), 'coerce')
    routes_df['Dest Airport ID'] = pd.to_numeric(
        routes_df['Dest Airport ID'].astype(str), 'coerce')
    routes_df = routes_df.dropna(
        subset=["Source Airport ID", "Dest Airport ID"])
    logger.info('Cleaned airports and routes')
