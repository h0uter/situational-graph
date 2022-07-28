import numpy as np

from src.data_providers.sim.simulated_agent import SimulatedAgent


def test_calc_heading_to_target_180():
    agent = SimulatedAgent()

    agent.pos = (1, 0)
    target_pos = (-1, 0)

    heading = agent.calc_heading_to_target(target_pos)

    assert heading == np.pi


def test_calc_heading_to_target_45():
    agent = SimulatedAgent()

    agent.pos = (1, 0)
    target_pos = (1, -1)

    heading = agent.calc_heading_to_target(target_pos)

    assert heading == np.pi * 1.5


def test_calc_heading_to_target_45_agent_at_0_0():
    agent = SimulatedAgent()

    agent.pos = (0, 0)
    target_pos = (1, -1)

    heading = agent.calc_heading_to_target(target_pos)

    assert heading == np.pi * (7/4)


def test_calc_heading_to_target_180_agent_at_0_0():
    agent = SimulatedAgent()

    agent.pos = (0, 0)
    target_pos = (-1, 0)

    heading = agent.calc_heading_to_target(target_pos)

    assert heading == np.pi


def test_calc_heading_to_target_270_agent_at_0_0():
    agent = SimulatedAgent()

    agent.pos = (0, 0)
    target_pos = (0, -1)

    heading = agent.calc_heading_to_target(target_pos)

    assert heading == np.pi * 1.5


def test_calc_heading_to_target_90_agent_at_0_0():
    agent = SimulatedAgent()

    agent.pos = (0, 0)
    target_pos = (0, 1)

    heading = agent.calc_heading_to_target(target_pos)

    assert heading == np.pi * 0.5
