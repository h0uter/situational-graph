from datetime import datetime
import os

from src.configuration.config import Config, Scenario, PlotLvl
from src.usecases.sar_usecase import run_sar_usecase


def benchmark_func():
    cfg = Config(
        plot_lvl=PlotLvl.NONE,
        num_agents=1,
        scenario=Scenario.SIM_MAZE_MEDIUM,
        max_steps=150,
    )

    run_sar_usecase(cfg)


def basic_profiler_test():
    import cProfile
    import pstats

    func_name = "benchmark_func()"
    # prof_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.profile"
    prof_name = f"{datetime.now().strftime('%Y%m%d-%H%M')}.profile"

    path = os.path.join("benchmarking", "benchmarks", prof_name)

    # pr = cProfile.run(func_name, sort='tottime', filename=f"benchmarking{prof_name}.profile")
    pr = cProfile.run(func_name, sort="tottime", filename=path)
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


if __name__ == "__main__":
    basic_profiler_test()
