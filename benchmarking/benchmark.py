from datetime import datetime
import os
from src.entrypoints.demo import benchmark_func


def profiler_test():
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        # cProfile.run("run_benchmark()", sort="cumulative")
        test()
        # exploration_with_sampling_viz("none")

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()

def basic_profiler_test():
    import cProfile
    import pstats
    func_name = 'benchmark_func()'
    # prof_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.profile"
    prof_name = f"{datetime.now().strftime('%Y%m%d-%H%M')}.profile"

    path = os.path.join("benchmarking","benchmarks", prof_name)

    # pr = cProfile.run(func_name, sort='tottime', filename=f"benchmarking{prof_name}.profile")
    pr = cProfile.run(func_name, sort='tottime', filename=path)
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()

def main():
    import cProfile
    import pstats
    from src.entrypoints.demo_sim import exploration_with_sampling_viz

    with cProfile.Profile() as pr:
        # cProfile.run("run_benchmark()", sort="cumulative")

        exploration_with_sampling_viz("none")

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()

if __name__ == "__main__":
    # main()
    # profiler_test()
    # basic_timing()
    basic_profiler_test()
