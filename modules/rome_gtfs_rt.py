import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2
from modules.colors import IN_TRANSIT_CL, LATE_CL, ON_TIME_CL, STOPPED_CL
from modules.constants import CORS_GTFS_TRIP_UPDATES, CORS_GTFS_VEHICLE_POS
from modules.time_utils import timestamp_to_hms
from pyproj import Transformer

# Vehicle Dataframe schema
VEHICLE_DF_COLUMNS = [
    "x",
    "y",
    "vehicleID",
    "tripID",
    "startTime",
    "lastUpdate",
    "currentStatus",
    "currentStatusClass",
    "statusColor",
]

VEHICLE_DF_SCHEMA = pd.DataFrame([], columns=VEHICLE_DF_COLUMNS)

# Delay Dataframe schema
DELAY_DF_COLUMNS = [
    "tripID",
    "delay",
    "delayClass",
    "delayColor",
]

DELAY_DF_SCHEMA = pd.DataFrame([], columns=DELAY_DF_COLUMNS)

FULL_DF_SCHEMA = VEHICLE_DF_SCHEMA.merge(DELAY_DF_SCHEMA, on="tripID")

# A transformer that converts coordinates from EPSG:4326 to EPSG:3857
transformer = Transformer.from_crs(4326, 3857, always_xy=True)


def build_url(cache_bust):
    """
    Get the current local time and build the request url
    """

    vehicle_url = CORS_GTFS_VEHICLE_POS + f"?cacheBust={cache_bust}"
    trip_url = CORS_GTFS_TRIP_UPDATES + f"?cacheBust={cache_bust}"

    return (vehicle_url, trip_url)


def get_vehicle_position(entity):
    """
    Returns the xy position of the processed entity.
    """

    coords = transformer.transform(
        entity.vehicle.position.longitude, entity.vehicle.position.latitude
    )
    return coords


def get_current_status_color(current_status):
    """
    Returns the color of the entity according to the status
    of the vehicle (In transit/Stopped).
    """

    return STOPPED_CL if current_status == 1 else IN_TRANSIT_CL


def get_current_status_class(current_status):
    """
    Returns the Vehicle current status (In transit/Stopped).
    """

    return "Stopped" if current_status == 1 else "In Transit"


def get_delay_color(delay):
    """
    Returns the color of the entity according to the delay class.
    """

    if delay <= 0:
        return ON_TIME_CL
    else:
        return LATE_CL


def get_delay_class(delay):
    """
    Returns the delay class (Late or On time).
    """

    if delay <= 0:
        return "On time"
    else:
        return "Late"


def get_vehicle_data(url):
    """Reads the vehicle position feed and returns a pandas DataFrame"""

    vehicle_feed = gtfs_realtime_pb2.FeedMessage()

    # TODO: Retry after the exception
    try:
        response = requests.get(url).content
        vehicle_feed.ParseFromString(response)
    except Exception as e:
        # We return an empty DataFrame
        return VEHICLE_DF_SCHEMA

    positions = []
    for entity in vehicle_feed.entity:
        # Vehicle attributes
        x, y = get_vehicle_position(entity)
        vehicle_id = entity.vehicle.vehicle.id
        trip_id = entity.vehicle.trip.trip_id.strip()
        start_time = entity.vehicle.trip.start_time
        last_update = timestamp_to_hms(entity.vehicle.timestamp)
        current_status = entity.vehicle.current_status
        current_status_class = get_current_status_class(current_status)
        vehicle_color = get_current_status_color(current_status)

        positions.append(
            [
                x,
                y,
                vehicle_id,
                trip_id,
                start_time,
                last_update,
                current_status,
                current_status_class,
                vehicle_color,
            ]
        )

    data = pd.DataFrame(positions, columns=VEHICLE_DF_COLUMNS)
    return data


def get_delay_data(url):
    """Reads the trip updates feed and returns a pandas DataFrame"""
    trip_update_feed = gtfs_realtime_pb2.FeedMessage()

    # TODO: Retry after the exception
    try:
        response = requests.get(url).content
        trip_update_feed.ParseFromString(response)
    except Exception as e:
        # We return an empty DataFrame
        return DELAY_DF_SCHEMA

    delays = []
    for entity in trip_update_feed.entity:
        trip_id = entity.trip_update.trip.trip_id.strip()
        current_stop_arrival = entity.trip_update.stop_time_update[0].arrival
        current_stop_delay = current_stop_arrival.delay / 60
        delay_class = get_delay_class(current_stop_delay)
        delay_color = get_delay_color(current_stop_delay)
        delays.append([trip_id, current_stop_delay, delay_class, delay_color])
    data = pd.DataFrame(delays, columns=DELAY_DF_COLUMNS)
    return data


def get_data(cache_bust):
    """
    This function reads the Roma mobilità GTFS-RT feed
    and returns a pandas DataFrame.
    """

    vehicle_url, trip_url = build_url(cache_bust)
    vehicle_data = get_vehicle_data(vehicle_url)
    delay_data = get_delay_data(trip_url)

    # Merge vehicle and delay dataframe
    full_data = vehicle_data.merge(delay_data, on="tripID")
    return full_data
