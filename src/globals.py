import os
from dotenv import load_dotenv
import supervisely as sly


if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

api = sly.Api()
project_id = sly.env.project_id()
project_meta_json = api.project.get_meta(project_id)
project_meta = sly.ProjectMeta.from_json(project_meta_json)
project_info = api.project.get_info_by_id(project_id)
dataset_id = sly.env.dataset_id(raise_not_found=False)
dataset_info = None
images = []
_class_filters = [
    {"field": "shape", "operator": "!=", "value": "line"},
    {"field": "shape", "operator": "!=", "value": "point"},
]
classes = api.object_class.get_list(project_id)

if not dataset_id is None:
    dataset_info = api.dataset.get_info_by_id(dataset_id)
    images = api.image.get_list(dataset_id)
else:
    datasets = api.dataset.get_list(project_id=project_id)
    for dataset in datasets:
        images.extend(api.image.get_list(dataset_id=dataset.id))

parents_names = []
childs_names = []
threshold = 0
