from src.shared.prior_knowledge.behaviors import Behaviors
from src.execution_autonomy.behaviors.explore_behavior import ExploreBehavior
from src.execution_autonomy.behaviors.goto_behavior import GotoBehavior
from src.execution_autonomy.behaviors.assess_behavior import AssessBehavior

# FIXME: generate this dynamically, or in cfg
SAR_BEHAVIORS = {
    Behaviors.EXPLORE: ExploreBehavior,
    Behaviors.GOTO: GotoBehavior,
    Behaviors.ASSESS: AssessBehavior,
}
