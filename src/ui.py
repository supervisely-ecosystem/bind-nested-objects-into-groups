from supervisely.app.widgets import (
    Card,
    Container,
    Button,
    ProjectThumbnail,
    DatasetThumbnail,
    Progress,
    InputNumber,
    Field,
    ObjectClassView,
    Select,
    NotificationBox,
)
import src.globals as g
import src.services as services


if g.dataset_id is None:
    thumbnail = ProjectThumbnail(g.project_info)
else:
    thumbnail = DatasetThumbnail(g.project_info, g.dataset_info)
thumbnail_card = Card(title="Input", content=thumbnail)

object_classes = [ObjectClassView(cl) for cl in g.classes]
action_input = [
    Select(
        items=[
            Select.Item("skip", "do nothing"),
            Select.Item("parent", "parent"),
            Select.Item("child", "child"),
        ]
    )
    for _ in g.classes
]

threshold_input = InputNumber(value=100)
threshold_field = Field(content=threshold_input, title="Threshold")

configuration = Container(
    widgets=[
        *[
            Container(
                widgets=[object_classes[i], action_input[i]],
                direction="horizontal",
                fractions=[1, 1],
            )
            for i in range(len(g.classes))
        ],
        threshold_field,
    ]
)

configuration_card = Card(title="Configuration", content=configuration)

progress_bar = Progress()

start_button = Button("start")
disclaimer = NotificationBox(
    title="Warning",
    description="Objects will be modified in-place! Make sure you backed up your data.",
    box_type="warning",
)
start_button_cont = Container(
    widgets=[
        disclaimer,
        start_button,
        progress_bar,
    ]
)
start_button_card = Card(content=start_button_cont)


@start_button.click
def start():
    parents = []
    childs = []
    for i in range(len(g.classes)):
        val = action_input[i].get_value()
        if val == "parent":
            parents.append(g.classes[i].name)
        elif val == "child":
            childs.append(g.classes[i].name)
    if len(childs) == 0:
        return
    if len(parents) == 0:
        return
    g.threshold = threshold_input.get_value() / 100
    g.parents_names = parents
    g.childs_names = childs
    with progress_bar(message="Processing items...", total=len(g.images)) as pbar:
        for image in g.images:
            services.bind_nested_objects_on_image(image.id)
            pbar.update(1)
