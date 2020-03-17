import pandas as pd
import logging
from typing import List, TextIO, Tuple
import importlib.resources as pkg_resources
import data


def flight_network_dataset() -> Tuple[pd.DataFrame, pd.DataFrame]:
    logger = logging.getLogger(__name__)

    # download airport info data
    airports_col = [
        'ID', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Lat', 'Long', 'Alt',
        'Timezone', 'DST', 'Tz database time zone', 'type', 'source'
    ]  # type: List[str]
    airports_path = pkg_resources.open_text(data,
                                            'airports.dat')  # type: TextIO
    airports_df = pd.read_csv(airports_path, names=airports_col,
                              index_col=0)  # type: pd.DataFrame
    logger.debug('Loaded airports.dat')

    # download flight routes data
    routes_cols = [
        'Airline', 'Airline ID', 'Source Airport', 'Source Airport ID',
        'Dest Airport', 'Dest Airport ID', 'Codeshare', 'Stops', 'equipment'
    ]  # type: List[str]
    routes_path = pkg_resources.open_text(data, 'routes.dat')  # type: TextIO
    routes_df = pd.read_csv(routes_path,
                            names=routes_cols)  # type: pd.DataFrame
    logger.debug('Loaded routes.dat')

    # clean up data, change 'object' type to numeric and drop NaNs
    routes_df['Source Airport ID'] = pd.to_numeric(
        routes_df['Source Airport ID'].astype(str), 'coerce')
    routes_df['Dest Airport ID'] = pd.to_numeric(
        routes_df['Dest Airport ID'].astype(str), 'coerce')
    routes_df = routes_df.dropna(
        subset=["Source Airport ID", "Dest Airport ID"])
    logger.debug('Cleaned routes')

    return airports_df, routes_df


def main_philipp() -> None:
    logger = logging.getLogger(__name__)

    airports_df, routes_df = flight_network_dataset()  # type: Tuple[pd.DataFrame, pd.DataFrame]
    logger.info('Loaded airports and cleaned routes')
