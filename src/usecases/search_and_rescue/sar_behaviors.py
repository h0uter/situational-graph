from src.platform_autonomy.execution.behaviors.assess_behavior import AssessBehavior
from src.platform_autonomy.execution.behaviors.explore_behavior import ExploreBehavior
from src.platform_autonomy.execution.behaviors.goto_behavior import GotoBehavior
from src.shared.prior_knowledge.sar_behaviors import Behaviors

# FIXME: generate this dynamically, or in cfg
SAR_BEHAVIORS = {
    Behaviors.EXPLORE: ExploreBehavior,
    Behaviors.GOTO: GotoBehavior,
    Behaviors.ASSESS: AssessBehavior,
}
