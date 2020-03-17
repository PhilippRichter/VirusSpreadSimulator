import pandas as pd
import logging
from typing import List, TextIO, Tuple, Dict
import importlib.resources as pkg_resources
import data
import plotly.graph_objects as go
import numpy as np


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


def add_start_end_geocoordinates_to_routes(
        airports_df: pd.DataFrame, routes_df: pd.DataFrame) -> pd.DataFrame:
    logger = logging.getLogger(__name__)

    airports_coordinates = {}
    for airport in airports_df.itertuples():
        airport_iata = airport[4]  # Airport IATA
        airport_long = airport[6]  # Airport Longitude
        airport_lat = airport[7]  # Airport Latitude
        single_airport_coordinates = {'long': airport_long, 'lat': airport_lat}
        airports_coordinates[airport_iata] = single_airport_coordinates
    routes_geocoordinates = {
        'start_long': [],
        'start_lat': [],
        'end_long': [],
        'end_lat': []
    }  # type: Dict[str, List[float]]
    found_airports = 0
    missing_airports = 0

    for route in routes_df.itertuples():
        start_airport_iata = route[3]  # Route Start Airport IATA
        end_airport_iata = route[5]  # Route End Airport IATA

        try:
            start_airport_coordinates = airports_coordinates[
                start_airport_iata]
            found_airports = found_airports + 1
            end_airport_coordinates = airports_coordinates[end_airport_iata]
            found_airports = found_airports + 1
        except KeyError as err:
            start_airport_coordinates = {'long': np.nan, 'lat': np.nan}
            end_airport_coordinates = {'long': np.nan, 'lat': np.nan}
            missing_airports = missing_airports + 1

        routes_geocoordinates['start_long'].append(
            start_airport_coordinates['long'])
        routes_geocoordinates['start_lat'].append(
            start_airport_coordinates['lat'])
        routes_geocoordinates['end_long'].append(
            end_airport_coordinates['long'])
        routes_geocoordinates['end_lat'].append(end_airport_coordinates['lat'])

    logger.info(
        f'Found airports during route geocoordinate resolution: {found_airports}'
    )
    logger.info(
        f'Missing airports during route geocoordinate resolution: {missing_airports}'
    )

    routes_df['start_long'] = routes_geocoordinates['start_long']
    routes_df['start_lat'] = routes_geocoordinates['start_lat']
    routes_df['end_long'] = routes_geocoordinates['end_long']
    routes_df['end_lat'] = routes_geocoordinates['end_lat']

    return routes_df


def plot_flight_network(airports_df: pd.DataFrame,
                        routes_df: pd.DataFrame) -> None:

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(locationmode='USA-states',
                      lon=airports_df['Long'],
                      lat=airports_df['Lat'],
                      hoverinfo='text',
                      text=airports_df['Name'],
                      mode='markers',
                      marker=dict(size=2,
                                  color='rgb(255, 0, 0)',
                                  line=dict(width=3,
                                            color='rgba(68, 68, 68, 0)'))))

    for route in routes_df.head(100).itertuples():
        fig.add_trace(
            go.Scattergeo(
                locationmode='USA-states',
                lon=[route[10], route[12]], # start_lon, end_lon
                lat=[route[11], route[13]], # start_lat, end_lat
                mode='lines',
                line=dict(width=1, color='red')
            ))

    fig.update_layout(
        title_text='Flight paths<br>(Hover for airport names)',
        showlegend=False,
        geo=dict(
            scope='north america',
            projection_type='azimuthal equal area',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        ),
    )

    fig.show()


def main_philipp() -> None:
    logger = logging.getLogger(__name__)

    airports_df, routes_df = flight_network_dataset(
    )  # type: Tuple[pd.DataFrame, pd.DataFrame]
    logger.info('Loaded airports and cleaned routes')

    routes_df = add_start_end_geocoordinates_to_routes(airports_df, routes_df)
    logger.info('Added start and end geocoordinates to routes')

    plot_flight_network(airports_df, routes_df)
    logger.info('Plotted network')
