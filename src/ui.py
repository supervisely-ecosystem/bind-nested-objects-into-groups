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
    Table,
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
        Select.Item(name, name, tag_input._input_widget)
        for name, tag_input in tag_meta_name_to_input.items()
    ],
]
tag_no_child_selector = Select(items=tag_no_child_items)
tag_no_child_input = OneOf(tag_no_child_selector)
tag_no_child_field = Field(
    content=Container(widgets=[tag_no_child_selector, tag_no_child_input]),
    title="Add tag if parent object has no children",
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

configuration_card = Card(
    title="Configuration",
    content=configuration,
    description="Select which classes to be parents and which classes to be children",
)

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

results_table = Table(
    columns=["image", "parents with children", "parents w/o children"]
)
results_table_card = Card(
    title="Images with issues",
    content=results_table,
    description="List of images with parent objects that have 0 child objects",
)
results_table_card.hide()


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


def _get_children():
    children = []
    for i, obj_class in enumerate(g.obj_classes):
        val = action_inputs[i].get_value()
        if val == "child":
            children.append(obj_class.name)
    return children


@start_button.click
def start():
    results_table_card.hide()
    for _ in range(len(g.images)):
        results_table.pop_row()
    success_message.hide()
    parents = _get_parents()
    children = _get_children()
    if len(children) == 0:
        return
    if len(parents) == 0:
        return
    threshold = threshold_input.get_value() / 100
    tag_no_child = _get_tag_no_child()
    show_table_flag = False
    with progress_bar(message="Processing items...", total=len(g.images)) as pbar:
        for image in g.images:
            (
                parents_with_children,
                parents_without_children,
            ) = services.bind_nested_objects_on_image(
                image_id=image.id,
                parents=parents,
                children=children,
                threshold=threshold,
                tag_no_child=tag_no_child,
            )
            image_labeling_url = f"{g.api.server_address}/app/images/{g.team_id}/{g.workspace_id}/{g.project_id}/{image.dataset_id}#image-{image.id}"
            html_url = f'<a href="{image_labeling_url}">{image.name} <i class="zmdi zmdi-open-in-new"></i></a>'
            if parents_without_children > 0:
                show_table_flag = True
                results_table.insert_row(
                    data=[
                        html_url,
                        parents_with_children,
                        parents_without_children,
                    ]
                )
            pbar.update(1)

    if show_table_flag:
        results_table_card.show()
    success_message.show()
