from datetime import datetime as dt

import pandas as pd
from constants import CORS_GTFS_RT_FEED, IN_TRANSIT_CL, STOPPED_CL
from google.transit import gtfs_realtime_pb2
from js import XMLHttpRequest
from pyproj import Transformer

# Dataframe schema
DF_COLUMNS = [
    "x",
    "y",
    "vehicleID",
    "label",
    "startTime",
    "lastUpdate",
    "currentStatus",
    "pointColor",
]

DF_SCHEMA = pd.DataFrame([], columns=DF_COLUMNS)

# Converts coordinates from EPSG:4326 to EPSG:3857
transformer = Transformer.from_crs(4326, 3857, always_xy=True)


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


def build_url():
    """
    Get the current local time and build the request url
    """

    time = dt.now().strftime("%H:%M:%S")
    url = CORS_GTFS_RT_FEED + f"?cacheBust={time}"
    return url


def read_feed():
    """
    HTTP request used to retrieve binary data from
    Roma mobilità GTFS-RT feed.
    """

    url = build_url()

    xhr = XMLHttpRequest.new()
    xhr.open("GET", url, False)
    xhr.overrideMimeType("text/plain; charset=x-user-defined")
    xhr.responseIsBinary = True
    xhr.send(None)
    return bytes(ord(byte) & 0xFF for byte in xhr.response)


def get_data():
    """
    This function reads the Roma mobilità GTFS-RT feed
    and returns a pandas DataFrame.
    """

    feed = gtfs_realtime_pb2.FeedMessage()

    try:
        response = read_feed()
        feed.ParseFromString(response)
    except Exception as e:
        # We return an empty DataFrame
        return DF_SCHEMA

    positions = []
    for entity in feed.entity:
        x, y = get_vehicle_position(entity)
        vehicle_id = entity.vehicle.vehicle.id
        vehicle_label = entity.vehicle.vehicle.label.strip()
        start_time = entity.vehicle.trip.start_time
        last_update = dt.fromtimestamp(entity.vehicle.timestamp).strftime(
            "%H:%M:%S"
        )

        current_status = entity.vehicle.current_status
        vehicle_color = get_current_status_color(current_status)
        positions.append(
            [
                x,
                y,
                vehicle_id,
                vehicle_label,
                start_time,
                last_update,
                current_status,
                vehicle_color,
            ]
        )
    data = pd.DataFrame(positions, columns=DF_COLUMNS)
    return data
