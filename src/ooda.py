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
        decision_model = self.initialization

        while True:
            orientation_model = self.observe()
            decision_model = self.orient(decision_model, orientation_model)
            execution_model = self.decide(decision_model)
            decision_model = self.act(execution_model)
