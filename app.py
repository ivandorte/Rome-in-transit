import holoviews as hv
import numpy as np
import panel as pn
import requests
from bokeh.models import HoverTool
from holoviews.streams import Pipe
from modules.colors import HEADER_CL
from modules.constants import ADMIN_BOUNDS, DASH_DESC
from modules.indicators import (
    FLEET_IND,
    IN_TRANSIT_IND,
    LATE_IND,
    ON_TIME_IND,
    STOPPED_IND,
)
from modules.rome_gtfs_rt import FULL_DF_SCHEMA, get_data
from modules.time_utils import get_current_time

# Load the bokeh extension
hv.extension("bokeh")

# Disable webgl: https://github.com/holoviz/panel/issues/4855
hv.renderer("bokeh").webgl = False  # Disable Webgl

# Set the sizing mode
pn.config.sizing_mode = "stretch_both"


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

    status_points = hv.DynamicMap(hv.Points, streams=[gtfs_pipe])
    status_points.opts(
        frame_width=600,
        frame_height=650,
        xaxis=None,
        yaxis=None,
        color="statusColor",
        line_alpha=0.0,
        fill_alpha=0.6,
        size=6,
        tools=[gtfs_hover],
    )

    delay_points = hv.DynamicMap(hv.Points, streams=[gtfs_pipe])
    delay_points.opts(
        frame_width=600,
        frame_height=650,
        xaxis=None,
        yaxis=None,
        color="delayColor",
        line_alpha=0.0,
        fill_alpha=0.6,
        size=6,
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

    curr_time = get_current_time()
    cache_bust = curr_time.split()[-1]
    data = get_data(cache_bust)
    if len(data):
        # Push the data into dynamic maps
        gtfs_pipe.send(data)

        # Update the widgets
        IN_TRANSIT_IND.value = data["currentStatus"].isin([2]).sum(axis=0)
        STOPPED_IND.value = data["currentStatus"].isin([1]).sum(axis=0)
        FLEET_IND.value = IN_TRANSIT_IND.value + STOPPED_IND.value

        ON_TIME_IND.value = data["delayClass"].isin(["On time"]).sum(axis=0)
        LATE_IND.value = data["delayClass"].isin(["Late"]).sum(axis=0)

        latest_update_time.value = get_current_time()
        alert_pane.visible = False
    else:
        latest_update_time.value = get_current_time()
        alert_pane.visible = True


# Description pane
desc_pane = pn.pane.HTML(
    DASH_DESC,
    styles={"text-align": "justified"},
    sizing_mode="stretch_width",
)

# Latest update time
latest_update_time = pn.widgets.StaticText(name="Latest Update")

# Indicators
status_indicators = pn.Row(IN_TRANSIT_IND, STOPPED_IND, FLEET_IND)
delay_indicators = pn.Row(ON_TIME_IND, LATE_IND)

# Alert pane
alert_pane = pn.pane.Alert("No data received from Roma mobilità!", alert_type="danger")
alert_pane.visible = False

# Inizialize the pipe
gtfs_pipe = Pipe(FULL_DF_SCHEMA)

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
        alert_pane,
        pn.Spacer(height=5),
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
