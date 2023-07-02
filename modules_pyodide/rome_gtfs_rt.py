from datetime import datetime as dt

import pandas as pd

# import requests
from constants import (
    CORS_GTFS_TRIP_UPDATES,
    CORS_GTFS_VEHICLE_POS,
    EU_ROME_TZ,
    IN_TRANSIT_CL,
    LATE_CL,
    ON_TIME_CL,
    STOPPED_CL,
)
from google.transit import gtfs_realtime_pb2
from js import XMLHttpRequest
from pyproj import Transformer

# Vehicle Dataframe schema
VEHICLE_DF_COLUMNS = [
    "x",
    "y",
    "vehicleID",
    "label",
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

# Converts coordinates from EPSG:4326 to EPSG:3857
transformer = Transformer.from_crs(4326, 3857, always_xy=True)


def build_url():
    """
    Get the current local time and build the request url
    """

    time = dt.now(EU_ROME_TZ).strftime("%H:%M:%S")
    vehicle_url = CORS_GTFS_VEHICLE_POS + f"?cacheBust={time}"
    trip_url = CORS_GTFS_TRIP_UPDATES + f"?cacheBust={time}"

    return (vehicle_url, trip_url)


def read_feed_xhr(url):
    """
    HTTP request used to retrieve binary data from
    Roma mobilità GTFS-RT feed (XHR).
    Adapted from: https://bartbroere.eu/2022/04/25/pyodide-requests-binary-works-update/
    """

    xhr = XMLHttpRequest.new()
    xhr.open("GET", url, False)
    xhr.overrideMimeType("text/plain; charset=x-user-defined")
    xhr.responseIsBinary = True
    xhr.send(None)

    response = xhr.response

    return bytes(ord(byte) & 0xFF for byte in response)


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
        response = read_feed_xhr(url)
        vehicle_feed.ParseFromString(response)
    except Exception as e:
        # We return an empty DataFrame
        return VEHICLE_DF_SCHEMA

    positions = []
    for entity in vehicle_feed.entity:
        # Vehicle attributes
        x, y = get_vehicle_position(entity)
        vehicle_id = entity.vehicle.vehicle.id
        vehicle_label = entity.vehicle.vehicle.label.strip()
        trip_id = entity.vehicle.trip.trip_id.strip()
        start_time = entity.vehicle.trip.start_time
        last_update = dt.fromtimestamp(
            entity.vehicle.timestamp, tz=EU_ROME_TZ
        ).strftime("%H:%M:%S")
        current_status = entity.vehicle.current_status
        current_status_class = get_current_status_class(current_status)
        vehicle_color = get_current_status_color(current_status)

        positions.append(
            [
                x,
                y,
                vehicle_id,
                vehicle_label,
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
        response = read_feed_xhr(url)
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


def get_data():
    """
    This function reads the Roma mobilità GTFS-RT feed
    and returns a pandas DataFrame.
    """

    vehicle_url, trip_url = build_url()
    vehicle_data = get_vehicle_data(vehicle_url)
    delay_data = get_delay_data(trip_url)

    # Merge vehicle and delay dataframe
    full_data = vehicle_data.merge(delay_data, on="tripID")
    return full_data
