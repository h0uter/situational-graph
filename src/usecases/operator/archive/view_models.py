@dataclass
class SituationalGraphViewModel:
    nodes: list
    edges: list


@dataclass
class PlanViewModel:
    plan: list[Edge]


@dataclass
class PlatformViewModel:
    pos: tuple
    heading: float


@dataclass
class ExplorationViewModel:
    local_grid_img: list
    lines: list
    collision_points: list
    frontiers: list
    waypoints: list