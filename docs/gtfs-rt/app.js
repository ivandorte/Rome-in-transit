importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['markdown-it-py<3', 'https://cdn.holoviz.org/panel/1.1.0/dist/wheels/bokeh-3.1.1-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.1.0/dist/wheels/panel-1.1.0-py3-none-any.whl', 'pyodide-http==0.2.1', 'holoviews>=1.15.4', 'holoviews', 'numpy', 'requests',  'pandas', 'pyproj', 'https://cdn.jsdelivr.net/gh/ivandorte/Rome-in-transit@main/wheels/gtfs_realtime_bindings-1.0.0-py3-none-any.whl', 'https://cdn.jsdelivr.net/gh/ivandorte/Rome-in-transit@main/wheels/protobuf-4.23.3-py3-none-any.whl', 'https://cdn.jsdelivr.net/gh/ivandorte/Rome-in-transit@main/wheels/pytz-2023.3-py2.py3-none-any.whl']
  for (const pkg of env_spec) {
    console.log(pkg);
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }

  // Load custom Python modules
  const custom_modules = ['https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/modules_pyodide/constants.py', 'https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/modules_pyodide/rome_gtfs_rt.py']
  for (const module of custom_modules) {
    let module_name;
    module_name = module.split('/').slice(-1)[0]
    await pyodide.runPythonAsync(`
        from pyodide.http import pyfetch
        module_pyodide = await pyfetch('${module}')
        with open('${module_name}', 'wb') as f:
            f.write(await module_pyodide.bytes())
      `);
  }
  
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

from datetime import datetime as dt

import json
import holoviews as hv
import numpy as np
import panel as pn
from bokeh.models import HoverTool
from holoviews.streams import Pipe
from constants import (
    ADMIN_BOUNDS,
    DASH_DESC,
    EU_ROME_TZ,
    FILL_ALPHA,
    HEADER_CL,
    IN_TRANSIT_CL,
    LATE_CL,
    LN_ALPHA,
    ON_TIME_CL,
    PT_SIZE,
    STOPPED_CL,
)
from pyodide.http import open_url
from rome_gtfs_rt import FULL_DF_SCHEMA, get_data
from pytz import timezone

# Load the bokeh extension
hv.extension("bokeh")

# Set the sizing mode
pn.config.sizing_mode = "stretch_both"


def get_current_time():
    """
    Returns the current date and time (Europe/Rome timezone).
    """

    rome_now = dt.now(EU_ROME_TZ).strftime("%d/%m/%Y %H:%M:%S")
    return rome_now


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

    delay_points = hv.DynamicMap(hv.Points, streams=[pipe])
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


await write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.globals.set('patch', msg.patch)
    self.pyodide.runPythonAsync(`
    state.curdoc.apply_json_patch(patch.to_py(), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.globals.set('location', msg.location)
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads(location)
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()