from src.domain.services.behaviors.explore_behavior import ExploreBehavior
from src.domain.services.behaviors.goto_behavior import GotoBehavior
from src.domain import Behaviors

# FIXME: generate this dynamically, or in cfg
BEHAVIOR_IMPLEMENTATIONS = {
    Behaviors.EXPLORE: ExploreBehavior,
    Behaviors.GOTO: GotoBehavior,
}
