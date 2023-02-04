import panel as pn
from constants import DASH_DESC

# Dashboard description HTML pane
DESC_PANE = pn.pane.HTML(
    DASH_DESC,
    style={"text-align": "justified"},
    sizing_mode="stretch_width",
)

# Latest update widget
LAST_UPDATE = pn.widgets.StaticText(name="Latest Update")
