from src.mission_autonomy.mission_runner import MissionRunner
from src.operator import runner
from src.platform_autonomy.platform_runner import PlatformRunner

if __name__ == "__main__":
    # matplotlib.use("Qt5agg")

    runner.run()

    # ImageMapDebugView()
    PlatformRunner()


    MissionRunner().mission_main_loop()

    # benchmark_func()
