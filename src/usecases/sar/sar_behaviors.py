from src.shared.behaviors import Behaviors
from src.usecases.shared.behaviors.explore_behavior import ExploreBehavior
from src.usecases.shared.behaviors.goto_behavior import GotoBehavior
from src.usecases.shared.behaviors.assess_behavior import AssessBehavior

# FIXME: generate this dynamically, or in cfg
SAR_BEHAVIORS = {
    Behaviors.EXPLORE: ExploreBehavior,
    Behaviors.GOTO: GotoBehavior,
    Behaviors.ASSESS: AssessBehavior,
}
