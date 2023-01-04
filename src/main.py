import supervisely as sly
from supervisely.app.widgets import Container
import src.ui as ui


layout = Container(
    widgets=[
        ui.thumbnail_card,
        ui.configuration_card,
        ui.start_button_card,
    ],
    direction="vertical",
    gap=15,
)

app = sly.Application(layout=layout)
