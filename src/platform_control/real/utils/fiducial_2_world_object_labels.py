# 202==201
from src.shared.world_object import WorldObject
from src.shared.prior_knowledge.situations import Situations

# FIXME: update this with the new world objects
# WORLD_OBJECT_ID_TO_NAME_MAPPING = {
#     "201": "victim1",
#     "202": "victim2",
#     "208": "fire1",
#     "207": "fire1",
#     "211": "victim2",
#     "212": "victim2",
# }

'''TNO'''
# WORLD_OBJECT_ID_TO_NAME_MAPPING = {
#     "204": Situations.UNKNOWN_VICTIM,
#     "205": Situations.UNKNOWN_VICTIM,
#     # "208": "fire1",
#     # "207": "fire1",
#     "206": Situations.UNKNOWN_VICTIM,
#     "207": Situations.UNKNOWN_VICTIM,
# }

'''TU Delft'''
WORLD_OBJECT_ID_TO_NAME_MAPPING = {
    "1": Situations.UNKNOWN_VICTIM,
    "3": Situations.UNKNOWN_VICTIM,
}


def create_wo_from_fiducial(pos: tuple[float, float], fiducial_id: int):

    if str(fiducial_id) in WORLD_OBJECT_ID_TO_NAME_MAPPING:
        name = WORLD_OBJECT_ID_TO_NAME_MAPPING[str(fiducial_id)]
        return WorldObject(pos, name)
    else:
        # print(f"create_wo_from_fiducial(): unknown fiducial {fiducial_id}")
        return None
