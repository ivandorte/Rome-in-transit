from datetime import datetime as dt

import holoviews as hv
import numpy as np
import panel as pn
import requests
from bokeh.models import HoverTool
from holoviews.streams import Pipe
from modules.constants import (
    ADMIN_BOUNDS,
    DASH_DESC,
    FILL_ALPHA,
    HEADER_CL,
    IN_TRANSIT_CL,
    LATE_CL,
    LN_ALPHA,
    ON_TIME_CL,
    PT_SIZE,
    STOPPED_CL,
)
from modules.rome_gtfs_rt import FULL_DF_SCHEMA, get_data

# Load the bokeh extension
hv.extension("bokeh")

# Set the sizing mode
pn.config.sizing_mode = "stretch_both"


def get_current_time():
    """
    Returns the current date and time.
    """
    return dt.now().strftime("%d/%m/%Y %H:%M:%S")


def init_stream_layers():
    """
    This function initialize the stream layers
    """

    gtfs_hover = HoverTool(
        tooltips=[
            ("Vehicle ID", "@vehicleID"),
            ("Trip ID", "@tripID"),
            ("Start Time", "@startTime"),
            ("Last Update", "@lastUpdate"),
            ("Delay (min)", "@delay"),
            ("Delay Class", "@delayClass"),
            ("Vehicle Status", "@currentStatusClass"),
        ]
    )

    status_points = hv.DynamicMap(hv.Points, streams=[pipe])
    status_points.opts(
        frame_width=600,
        frame_height=650,
        xaxis=None,
        yaxis=None,
        color="statusColor",
        line_alpha=LN_ALPHA,
        fill_alpha=FILL_ALPHA,
        size=PT_SIZE,
        tools=[gtfs_hover],
    )

    delay_points = hv.DynamicMap(hv.Points, streams=[pipe])
    delay_points.opts(
        frame_width=600,
        frame_height=650,
        xaxis=None,
        yaxis=None,
        color="delayColor",
        line_alpha=LN_ALPHA,
        fill_alpha=FILL_ALPHA,
        size=PT_SIZE,
        tools=[gtfs_hover],
    )
    return status_points, delay_points


def get_admin_bounds():
    """
    Returns a Path plot showing the Administrative boundaries
    of Rome.
    """

    admin_geojson = requests.get(ADMIN_BOUNDS).json()

    paths = hv.Path([])
    for fc in admin_geojson["features"][0]["geometry"]["coordinates"]:
        fc_path = hv.Path((np.array(fc)[:, 0], np.array(fc)[:, 1]))
        fc_path.opts(color="grey")
        paths *= fc_path
    return paths


def update_dashboard():
    """
    This function updates the Stream Layers and the number widgets
    """

    data = get_data()
    if len(data):
        # Push the data into dynamic maps
        pipe.send(data)

        # Update the widgets
        in_transit_ind.value = data["currentStatus"].isin([2]).sum(axis=0)
        stopped_ind.value = data["currentStatus"].isin([1]).sum(axis=0)
        fleet_ind.value = in_transit_ind.value + stopped_ind.value

        on_time_ind.value = data["delayClass"].isin(["On time"]).sum(axis=0)
        late_ind.value = data["delayClass"].isin(["Late"]).sum(axis=0)

        latest_update_time.value = get_current_time()


# Description pane
desc_pane = pn.pane.HTML(
    DASH_DESC,
    styles={"text-align": "justified"},
    sizing_mode="stretch_width",
)

# Latest update time
latest_update_time = pn.widgets.StaticText(name="Latest Update")

# TODO: Center the text
# In transit vehicles
in_transit_ind = pn.indicators.Number(
    value=0,
    name="In Transit",
    title_size="18pt",
    font_size="40pt",
    default_color="white",
    styles={"background": IN_TRANSIT_CL, "opacity": str(FILL_ALPHA)},
    sizing_mode="stretch_width",
)

# Stopped vehicles
stopped_ind = in_transit_ind.clone(name="Stopped", styles={"background": STOPPED_CL})

# Fleet (in transit + stopped)
fleet_ind = in_transit_ind.clone(name="Fleet", styles={"background": HEADER_CL})

# Vehicles on schedule
on_time_ind = in_transit_ind.clone(name="On Time", styles={"background": ON_TIME_CL})

# Vehicles behind schedule
late_ind = in_transit_ind.clone(name="Late", styles={"background": LATE_CL})

status_indicators = pn.Row(in_transit_ind, stopped_ind, fleet_ind)
delay_indicators = pn.Row(on_time_ind, late_ind)

# Inizialize the pipe
pipe = Pipe(FULL_DF_SCHEMA)

# Inizialize the stream layers
status_points, delay_points = init_stream_layers()

# CartoLight tiles
tiles = hv.element.tiles.CartoLight()

# Administrative boundaries of Rome
admin_bounds = get_admin_bounds()

# Stream layers
status_map = tiles * admin_bounds * status_points
delay_map = tiles * admin_bounds * delay_points

# Initialize the stream layers and indicators
update_dashboard()

# Define a periodic callback that updates the stream layers and the number widgets every 10 seconds
callback = pn.state.add_periodic_callback(callback=update_dashboard, period=10000)

# Compose the main layout
layout = pn.Row(
    pn.Column(
        desc_pane,
        status_indicators,
        pn.Spacer(height=25),
        delay_indicators,
        latest_update_time,
        width=400,
    ),
    pn.Tabs(
        ("Vehicle Status", status_map),
        ("Delays", delay_map),
    ),
)

# Turn into a deployable application
pn.template.FastListTemplate(
    site="",
    title="Rome in Transit",
    logo="https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/assets/train.svg",
    theme="default",
    theme_toggle=False,
    header_background=HEADER_CL,
    main_max_width="1100px",
    main=[layout],
).servable()
