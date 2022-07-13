from src.domain import Behaviors
from src.domain.services.behaviors.explore_behavior import ExploreBehavior
from src.domain.services.behaviors.goto_behavior import GotoBehavior
from src.domain.services.behaviors.assess_behavior import AssessBehavior

# FIXME: generate this dynamically, or in cfg
SAR_BEHAVIORS = {
    Behaviors.EXPLORE: ExploreBehavior,
    Behaviors.GOTO: GotoBehavior,
    Behaviors.ASSESS: AssessBehavior,
}
