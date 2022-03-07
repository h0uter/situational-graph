# 202==201
from src.entities.world_object import WorldObject


world_object_id_to_name_mapping = {
    "201": "victim1",
    "202": "victim1",
    "208": "fire1",
    "207": "fire1",
    "211": "victim2",
    "212": "victim2",
}


def create_wo_from_fiducial(pos, id):
    name = world_object_id_to_name_mapping[str(id)]
    return WorldObject(pos, name)
