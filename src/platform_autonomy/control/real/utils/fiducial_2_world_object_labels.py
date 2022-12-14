from src.config import cfg
from src.shared.world_object import WorldObject


def create_world_object_from_fiducial(pos: tuple[float, float], fiducial_id: int):

    if str(fiducial_id) in cfg.WORLD_OBJECT_ID_TO_NAME_MAPPING:
        name = cfg.WORLD_OBJECT_ID_TO_NAME_MAPPING[str(fiducial_id)]
        return WorldObject(pos, name)
    else:
        # print(f"create_wo_from_fiducial(): unknown fiducial {fiducial_id}")
        return None
