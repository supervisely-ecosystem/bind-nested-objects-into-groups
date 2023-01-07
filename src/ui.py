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
    Text,
    Empty,
    InputTag,
    OneOf,
)
from supervisely import TagApplicableTo
import src.globals as g
import src.services as services


if g.dataset_id is None:
    thumbnail = ProjectThumbnail(g.project_info)
else:
    thumbnail = DatasetThumbnail(g.project_info, g.dataset_info)
thumbnail_card = Card(title="Input", content=thumbnail)

object_classes_views = [ObjectClassView(cl) for cl in g.obj_classes]
action_inputs = [
    Select(
        items=[
            Select.Item("skip", "do nothing"),
            Select.Item("parent", "parent"),
            Select.Item("child", "child"),
        ]
    )
    for _ in g.obj_classes
]

threshold_input = InputNumber(value=100)
threshold_field = Field(content=threshold_input, title="Threshold, %")

objects_tag_metas = [
    tag_meta
    for tag_meta in g.project_meta.tag_metas
    if tag_meta.applicable_to in (TagApplicableTo.OBJECTS_ONLY, TagApplicableTo.ALL)
]
tag_meta_name_to_input = {tm.name: InputTag(tm) for tm in objects_tag_metas}
for input_tag in tag_meta_name_to_input.values():
    input_tag.activate()
tag_no_child_items = [
    Select.Item(None, "Do not add", Empty()),
    *[
        Select.Item(name, name, tag_input._component._content)
        for name, tag_input in tag_meta_name_to_input.items()
    ],
]
tag_no_child_selector = Select(items=tag_no_child_items)
tag_no_child_input = OneOf(tag_no_child_selector)
tag_no_child_field = Field(
    content=Container(widgets=[tag_no_child_selector, tag_no_child_input]),
    title="Add tag if parent object has no childs",
)

configuration = Container(
    widgets=[
        *[
            Container(
                widgets=[object_classes_views[i], action_inputs[i]],
                direction="horizontal",
                fractions=[1, 1],
            )
            for i in range(len(g.obj_classes))
        ],
        threshold_field,
        tag_no_child_field,
    ]
)

configuration_card = Card(title="Configuration", content=configuration)

progress_bar = Progress()

start_button = Button("start")
disclaimer = NotificationBox(
    title="Warning",
    description="Objects will be modified in-place!",
    box_type="warning",
)
success_message = Text("Done!", status="success")
success_message.hide()
start_button_cont = Container(
    widgets=[
        disclaimer,
        start_button,
        progress_bar,
        success_message,
    ]
)
start_button_card = Card(content=start_button_cont)


def _get_tag_no_child():
    tag_name = tag_no_child_selector.get_value()
    if tag_name is None:
        return None
    input = tag_meta_name_to_input[tag_name]
    tag = input.get_tag()
    return tag


def _get_parents():
    parents = []
    for i in range(len(g.obj_classes)):
        val = action_inputs[i].get_value()
        if val == "parent":
            parents.append(g.obj_classes[i].name)
    return parents


def _get_childs():
    childs = []
    for i, obj_class in enumerate(g.obj_classes):
        val = action_inputs[i].get_value()
        if val == "child":
            childs.append(obj_class.name)
    return childs


@start_button.click
def start():
    success_message.hide()
    parents = _get_parents()
    childs = _get_childs()
    if len(childs) == 0:
        return
    if len(parents) == 0:
        return
    tag_no_child = _get_tag_no_child()
    g.threshold = threshold_input.get_value() / 100
    g.parents_names = parents
    g.childs_names = childs
    with progress_bar(message="Processing items...", total=len(g.images)) as pbar:
        for image in g.images:
            services.bind_nested_objects_on_image(image.id, tag_no_child=tag_no_child)
            pbar.update(1)
    success_message.show()
