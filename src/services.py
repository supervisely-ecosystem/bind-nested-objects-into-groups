import supervisely as sly
import src.utils as utils
import src.globals as g


def _get_relations(parents, childs, threshold):
    relations = {}
    is_child = set()
    for ch_idx, ch_el in enumerate(childs):
        for par_idx, par_el in enumerate(parents):
            if ch_idx in is_child:
                break
            score = utils.get_labels_intersection_over_first(ch_el, par_el)
            if score >= threshold:
                is_child.add(ch_idx)
                if par_idx in relations:
                    if not ch_idx in relations[par_idx]:
                        relations[par_idx].append(ch_idx)
                else:
                    relations[par_idx] = [ch_idx]
    return relations


def bind_nested_objects_on_image(image_id: int):
    ann_json = g.api.annotation.download_json(image_id)
    ann = sly.Annotation.from_json(ann_json, g.project_meta)

    parents = []
    childs = []
    skipped = []
    for i, label in enumerate(ann.labels):
        if label.obj_class.name in g.parents_names:
            parents.append(i)
        elif label.binding_key is None:
            if label.obj_class.name in g.childs_names:
                childs.append(i)
            else:
                skipped.append(i)
        else:
            skipped.append(i)

    relations = _get_relations(
        [ann.labels[i] for i in parents],
        [ann.labels[i] for i in childs],
        g.threshold,
    )

    for parent_idx, childs_idxs in relations.items():
        key = str(ann.labels[parents[parent_idx]].to_json()["id"])
        ann.labels[parents[parent_idx]].binding_key = key
        for idx in childs_idxs:
            ann.labels[childs[idx]].binding_key = key

    first = []
    last = []
    for label in ann.labels:
        if label.binding_key == str(label.to_json()["id"]):
            last.append(label)
        else:
            first.append(label)
    for label in ann.labels:
        ann = ann.delete_label(label)
    ann = ann.add_labels([*first, *last])
    g.api.annotation.upload_ann(image_id, ann)
