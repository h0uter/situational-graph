
from knowledge_roadmap.entrypoints.demo_sim import exploration_with_sampling_viz

def test():
    print("hi")


def basic_timing():
    import time
    start = time.perf_counter()
    exploration_with_sampling_viz("none")
    elapsed = time.perf_counter() - start
    print(f"Elapsed time: {elapsed}")


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

    pr = cProfile.run('exploration_with_sampling_viz("intermediate only")', sort='tottime', filename="with_plotting.profile")
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()

def main():
    import cProfile
    import pstats
    from knowledge_roadmap.entrypoints.demo_sim import exploration_with_sampling_viz

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