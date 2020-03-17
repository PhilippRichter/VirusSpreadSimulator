import pandas as pd
import logging
from typing import List


def main() -> None:
    logger = logging.getLogger(__name__)

    # download airport info data
    airport_col = [
        'ID', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Lat', 'Long', 'Alt',
        'Timezone', 'DST', 'Tz database time zone', 'type', 'source'
    ]  # type: List[str]
    airport_df = pd.read_csv(
        "https://raw.githubusercontent.com/PhilippRichter/VirusSpreadSimulator/master/virusspreadsimulator/data/airports.dat",
        names=airport_col,
        index_col=0)  # type: pd.DataFrame
    logger.info('Downloaded airports.dat')

    # download flight routes data
    route_cols = [
        'Airline', 'Airline ID', 'Source Airport', 'Source Airport ID',
        'Dest Airport', 'Dest Airport ID', 'Codeshare', 'Stops', 'equipment'
    ]  # type: List[str]
    routes_df = pd.read_csv(
        "https://raw.githubusercontent.com/PhilippRichter/VirusSpreadSimulator/master/virusspreadsimulator/data/routes.dat",
        names=route_cols)  # type: pd.DataFrame
    logger.info('Downloaded routes.dat')

    # clean up data, change 'object' type to numeric and drops NaNs
    routes_df['Source Airport ID'] = pd.to_numeric(
        routes_df['Source Airport ID'].astype(str), 'coerce')
    routes_df['Dest Airport ID'] = pd.to_numeric(
        routes_df['Dest Airport ID'].astype(str), 'coerce')
    routes_df = routes_df.dropna(
        subset=["Source Airport ID", "Dest Airport ID"])
    logger.info('Cleaned airports and routes')
