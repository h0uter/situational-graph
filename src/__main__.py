from src.configuration.config import Config, PlotLvl, Scenario

from src.usecases.sar.sar_usecase import run_sar_usecase, run_task_switch_usecase


# TODO: move this config out of here to the config file itself
if __name__ == "__main__":
    # matplotlib.use("Qt5agg")

    run_sar_usecase()
    # run_task_switch_usecase(cfg)

    # benchmark_func()
