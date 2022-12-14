from src.mission_autonomy.mission_runner import MissionRunner
from src.operator import runner

if __name__ == "__main__":
    # matplotlib.use("Qt5agg")

    runner.run()

    # ImageMapDebugView()

    MissionRunner().mission_main_loop()

    # benchmark_func()
