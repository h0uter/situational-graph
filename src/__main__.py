from src.mission_autonomy.sar.search_and_rescue_usecase import SearchAndRescueUsecase
from src.operator import runner

if __name__ == "__main__":
    # matplotlib.use("Qt5agg")

    runner.run()

    # ImageMapDebugView()

    SearchAndRescueUsecase().mission_main_loop()

    # benchmark_func()
