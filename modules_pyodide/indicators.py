import panel as pn
from constants import HEADER_CL, IN_TRANSIT_CL, STOPPED_CL

# Number indicator - In transit vehicles
IN_TRANSIT_IND = pn.indicators.Number(
    value=0,
    name="In Transit",
    default_color="white",
    align="center",
    background=IN_TRANSIT_CL,
    sizing_mode="stretch_width",
    css_classes=["center_number"],
)

# Number indicator - Stopped vehicles
STOPPED_IND = pn.indicators.Number(
    value=0,
    name="Stopped",
    default_color="white",
    align="center",
    background=STOPPED_CL,
    sizing_mode="stretch_width",
    css_classes=["center_number"],
)

# Number indicator - Vehicle fleet (In transit + stopped)
FLEET_IND = pn.indicators.Number(
    value=0,
    name="Fleet",
    default_color="white",
    align="center",
    background=HEADER_CL,
    sizing_mode="stretch_width",
    css_classes=["center_number"],
)
