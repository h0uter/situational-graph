# 202==201
from src.domain.entities.world_object import WorldObject

# FIXME: update this with the new world objects
WORLD_OBJECT_ID_TO_NAME_MAPPING = {
    "201": "victim1",
    "202": "victim2",
    "208": "fire1",
    "207": "fire1",
    "211": "victim2",
    "212": "victim2",
}


def create_wo_from_fiducial(pos, fiducial_id):

    if str(fiducial_id) in WORLD_OBJECT_ID_TO_NAME_MAPPING:
        name = WORLD_OBJECT_ID_TO_NAME_MAPPING[str(fiducial_id)]
        return WorldObject(pos, name)
    else:
        # print(f"create_wo_from_fiducial(): unknown fiducial {fiducial_id}")
        return None
