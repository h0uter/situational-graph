from src.usecases.behaviors.explore_behavior import ExploreBehavior
from src.usecases.behaviors.goto_behavior import GotoBehavior
from src.entities import Behaviors

# FIXME: generate this dynamically, or in cfg
BEHAVIOR_IMPLEMENTATIONS = {
    Behaviors.EXPLORE: ExploreBehavior,
    Behaviors.GOTO: GotoBehavior,
}
