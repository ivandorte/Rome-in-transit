importScripts("https://cdn.jsdelivr.net/pyodide/v0.22.1/full/pyodide.js");

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
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.3/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.3/dist/wheels/panel-0.14.3-py3-none-any.whl', 'https://cdn.jsdelivr.net/gh/ivandorte/Rome-in-transit@main/packages_pyodide/gtfs_realtime_bindings-0.0.7-py3-none-any.whl', 'https://cdn.jsdelivr.net/gh/ivandorte/Rome-in-transit@main/packages_pyodide/protobuf-4.21.12-py3-none-any.whl', 'pyodide-http==0.1.0', 'holoviews>=1.15.4', 'numpy', 'pandas', 'pyproj']
  for (const pkg of env_spec) {
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

import json
from datetime import datetime as dt

import holoviews as hv
import numpy as np
import panel as pn
import requests
from bokeh.models import HoverTool
from holoviews.streams import Pipe
from constants import (
    ADMIN_BOUNDS,
    CSS_NUMIND,
    DASH_DESC,
    HEADER_CL,
    IN_TRANSIT_CL,
    STOPPED_CL,
)
from pyodide.http import open_url
from rome_gtfs_rt import DF_SCHEMA, get_data

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

# Define a PeriodicCallback that updates every 10 seconds with data retrieved from Roma mobilit?? GTFS-RT feed
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
    self.pyodide.runPythonAsync(`
    import json

    state.curdoc.apply_json_patch(json.loads('${msg.patch}'), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads("""${msg.location}""")
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()