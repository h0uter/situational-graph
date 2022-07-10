from src.domain import Behaviors
from src.domain.services.behaviors.explore_behavior import ExploreBehavior
from src.domain.services.behaviors.goto_behavior import GotoBehavior

# FIXME: generate this dynamically, or in cfg
SAR_BEHAVIORS = {
    Behaviors.EXPLORE: ExploreBehavior,
    Behaviors.GOTO: GotoBehavior,
}
