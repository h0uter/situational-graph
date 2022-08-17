from src.usecases.sar.sar_usecase import SearchAndRescueUseCase
from src.usecases.task_switch.task_switch_usecase import TaskSwitchUseCase

if __name__ == "__main__":
    # matplotlib.use("Qt5agg")

    # run_sar_usecase()
    # SearchAndRescueUseCase().run()
    # run_task_switch_usecase()
    TaskSwitchUseCase().run()

    # benchmark_func()
