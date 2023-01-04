from supervisely.app.widgets import (
    Card,
    Container,
    Button,
    ProjectThumbnail,
    DatasetThumbnail,
    Checkbox,
    Progress,
    InputNumber,
    Field,
)
import src.globals as g
import src.services as services


if g.dataset_id is None:
    thumbnail = ProjectThumbnail(g.project_info)
else:
    thumbnail = DatasetThumbnail(g.project_info, g.dataset_info)
thumbnail_card = Card(title="Input", content=thumbnail)

parents_checkboxes = [Checkbox(content=cl.name) for cl in g.classes]
parents_selector = Card(title="Parents", content=Container(widgets=parents_checkboxes))

childs_checkboxes = [Checkbox(content=cl.name) for cl in g.classes]
childs_selector = Card(title="Childs", content=Container(widgets=childs_checkboxes))

threshold_input = InputNumber()
threshold_field = Field(content=threshold_input, title="Threshold")

configuration = Container(
    widgets=[
        Container(widgets=[parents_selector, childs_selector], direction="horizontal"),
        threshold_field,
    ]
)

configuration_card = Card(title="Configuration", content=configuration)

progress_bar = Progress()

start_button = Button("start")


@start_button.click
def start():
    parents = [cb._content.text for cb in parents_checkboxes if cb.is_checked()]
    if len(parents) == 0:
        return
    childs = [cb._content.text for cb in childs_checkboxes if cb.is_checked()]
    if len(childs) == 0:
        return
    g.threshold = threshold_input.get_value() / 100
    g.parents_names = parents
    g.childs_names = childs
    with progress_bar(message="Processing items...", total=len(g.images)) as pbar:
        for image in g.images:
            services.bind_nested_objects_on_image(image.id)
            pbar.update(1)
