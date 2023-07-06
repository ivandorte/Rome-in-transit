import panel as pn
from colors import HEADER_CL, IN_TRANSIT_CL, LATE_CL, ON_TIME_CL, STOPPED_CL

# In transit vehicles
IN_TRANSIT_IND = pn.indicators.Number(
    value=0,
    name="In Transit",
    title_size="18pt",
    font_size="40pt",
    default_color="white",
    styles={
        "background": IN_TRANSIT_CL,
        "text-align": "center",
    },
    sizing_mode="stretch_width",
)

# Stopped vehicles
STOPPED_IND = IN_TRANSIT_IND.clone(
    name="Stopped",
    styles={
        "background": STOPPED_CL,
        "text-align": "center",
    },
)

# Fleet (in transit + stopped)
FLEET_IND = IN_TRANSIT_IND.clone(
    name="Fleet",
    styles={
        "background": HEADER_CL,
        "text-align": "center",
    },
)

# Vehicles on schedule
ON_TIME_IND = IN_TRANSIT_IND.clone(
    name="On Time",
    styles={
        "background": ON_TIME_CL,
        "text-align": "center",
    },
)

# Vehicles behind schedule
LATE_IND = IN_TRANSIT_IND.clone(
    name="Late",
    styles={
        "background": LATE_CL,
        "text-align": "center",
    },
)
