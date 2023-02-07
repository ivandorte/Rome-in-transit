import json
from datetime import datetime as dt

import holoviews as hv
import numpy as np
import panel as pn
from bokeh.models import HoverTool
from constants import (
    ADMIN_BOUNDS,
    CSS_NUMIND,
    DASH_DESC,
    HEADER_CL,
    IN_TRANSIT_CL,
    STOPPED_CL,
)
from holoviews.streams import Pipe
from pyodide.http import open_url
from rome_gtfs_rt import DF_SCHEMA, get_data

# import requests

# Load the bokeh extension
hv.extension("bokeh")

# Load Panel extensions
pn.extension()

# Set the sizing mode
pn.config.sizing_mode = "stretch_both"

pn.config.raw_css.append(CSS_NUMIND)


def get_current_time():
    """
    Returns the current date and time.
    """
    return dt.now().strftime("%d/%m/%Y %H:%M:%S")


def init_stream_layer():
    """
    This function initialize the GTFS-RT Stream Layer
    """

    gtfs_hover = HoverTool(
        tooltips=[
            ("vehicle ID", "@vehicleID"),
            ("Label", "@label"),
            ("Start Time", "@startTime"),
            ("Last Update", "@lastUpdate"),
        ]
    )

    points = hv.DynamicMap(hv.Points, streams=[pipe])
    points.opts(
        frame_width=500,
        frame_height=500,
        xaxis=None,
        yaxis=None,
        color="pointColor",
        line_alpha=0.0,
        fill_alpha=0.6,
        size=4,
        tools=[gtfs_hover],
    )
    return points


def get_admin_bounds():
    """
    Returns a Path plot showing the Administrative boundaries
    of Rome.
    """

    # admin_geojson = requests.get(ADMIN_BOUNDS).json()
    response = open_url(ADMIN_BOUNDS)
    admin_geojson = json.loads(response.getvalue())

    paths = hv.Path([])
    for fc in admin_geojson["features"][0]["geometry"]["coordinates"]:
        fc_path = hv.Path((np.array(fc)[:, 0], np.array(fc)[:, 1]))
        fc_path.opts(color="grey")
        paths *= fc_path
    return paths


def update_dashboard():
    """
    This function updates the Stream Layer and the widgets
    """

    data = get_data()
    if len(data):
        pipe.send(data)
        in_transit_numind.value = data["currentStatus"].isin([2]).sum(axis=0)
        stopped_numind.value = data["currentStatus"].isin([1]).sum(axis=0)
        fleet_numind.value = in_transit_numind.value + stopped_numind.value
        last_update.value = get_current_time()


# Dashboard description HTML pane
desc_pane = pn.pane.HTML(
    DASH_DESC,
    style={"text-align": "justified"},
    sizing_mode="stretch_width",
)

# Latest update widget
last_update = pn.widgets.StaticText(name="Latest Update")

# Number indicator - In transit vehicles
in_transit_numind = pn.indicators.Number(
    value=0,
    name="In Transit",
    default_color="white",
    align="center",
    background=IN_TRANSIT_CL,
    sizing_mode="stretch_width",
    css_classes=["center_number"],
)

# Number indicator - Stopped vehicles
stopped_numind = in_transit_numind.clone(name="Stopped", background=STOPPED_CL)

# Number indicator - Vehicle fleet (In transit + stopped)
fleet_numind = in_transit_numind.clone(name="Fleet", background=HEADER_CL)

# Inizialize the Stream Layer
pipe = Pipe(DF_SCHEMA)
points = init_stream_layer()

# Administrative boundaries of Rome
admin_bounds = get_admin_bounds()

# CartoLight tiles
tiles = hv.element.tiles.CartoLight()

# Main map view
map_elem = tiles * admin_bounds * points

# Initialize the map view
update_dashboard()

# Define a PeriodicCallback that updates every 10 seconds with data retrieved from Roma mobilità GTFS-RT feed
callback = pn.state.add_periodic_callback(
    callback=update_dashboard, period=10000
)

# Compose the main layout
layout = pn.Row(
    pn.Column(
        desc_pane,
        pn.Row(in_transit_numind, stopped_numind),
        fleet_numind,
        last_update,
        width=400,
    ),
    map_elem,
)

# Turn into a deployable application
pn.template.FastListTemplate(
    site="",
    title="Rome in Transit",
    logo="https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/assets/train.svg",
    theme="default",
    theme_toggle=False,
    header_background=HEADER_CL,
    main=[layout],
    main_max_width="1000px",
).servable()
