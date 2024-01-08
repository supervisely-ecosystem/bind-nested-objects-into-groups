import os
from dotenv import load_dotenv
import supervisely as sly


if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

api = sly.Api()
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()
project_id = sly.env.project_id()
project_meta_json = api.project.get_meta(project_id)
project_meta = sly.ProjectMeta.from_json(project_meta_json)
project_info = api.project.get_info_by_id(project_id)
dataset_id = sly.env.dataset_id(raise_not_found=False)
dataset_info = None
images = []

obj_classes = project_meta.obj_classes

if dataset_id is None:
    datasets = api.dataset.get_list(project_id=project_id)
    for dataset in datasets:
        images.extend(api.image.get_list(dataset_id=dataset.id))
else:
    dataset_info = api.dataset.get_info_by_id(dataset_id)
    images = api.image.get_list(dataset_id)
