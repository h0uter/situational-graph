# 202==201
from src.entities.world_object import WorldObject


world_object_id_to_name_mapping = {
    "201": "victim1",
    "202": "victim2",
    "208": "fire1",
    "207": "fire1",
    "211": "victim2",
    "212": "victim2",
}


def create_wo_from_fiducial(pos, fiducial_id):

    if str(fiducial_id) in world_object_id_to_name_mapping:
        name = world_object_id_to_name_mapping[str(fiducial_id)]
        return WorldObject(pos, name)
    else:
        # print(f"create_wo_from_fiducial(): unknown fiducial {fiducial_id}")
        return None
