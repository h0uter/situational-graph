from src.config import Scenario, cfg
from src.mission_autonomy.mission_runner import MissionRunner
from src.operator import operator_runner
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.control.real.spot_agent import SpotAgent
from src.platform_autonomy.control.sim.simulated_agent import SimulatedAgent
from src.platform_autonomy.platform_runner import PlatformRunner
from src.shared.prior_knowledge.capabilities import Capabilities
from src.shared.situational_graph import SituationalGraph
from src.usecases.search_and_rescue.exploration_mission_initializer import ExplorationMissionInitializer


def run_usecase():

    operator_runner.run()

    PlatformRunner()
    
    AGENT1_CAPABILITIES = {Capabilities.CAN_ASSESS}

    if cfg.SCENARIO == Scenario.REAL:
        agents = [SpotAgent(AGENT1_CAPABILITIES)]
    else:
        agents = [
            SimulatedAgent(AGENT1_CAPABILITIES)
        ]  # make the first agent only posses the capabilities
        agents.extend([SimulatedAgent(set(), i) for i in range(1, cfg.NUM_AGENTS)])
    
    # TODO: make it so that here we can also load an existing tosg.
    tosg = SituationalGraph()

    mission_initializer = ExplorationMissionInitializer()
    
    mission_runner = MissionRunner(agents, tosg, mission_initializer)
    mission_runner.mission_main_loop(agents, tosg)
