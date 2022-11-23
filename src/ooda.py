from dataclasses import dataclass


@dataclass
class OrientationModel:
    pass


@dataclass
class DecisionModel:
    pass


@dataclass
class ExecutionModel:
    pass


class OODA:
    def __init__(self, initialization: DecisionModel):

        self.initialization = initialization

    def observe(self) -> OrientationModel:
        pass

    def orient(
        self, decision_model: DecisionModel, orientation_model: OrientationModel
    ) -> DecisionModel:
        pass

    def decide(self, decision_model: DecisionModel) -> ExecutionModel:
        pass

    def act(self, execution_model: ExecutionModel) -> DecisionModel:
        pass

    def loop(self):
        plan_model = self.initialization

        while True:
            perception_model = self.observe()
            plan_model = self.orient(plan_model, perception_model)
            execution_model = self.decide(plan_model)
            plan_model = self.act(execution_model)
