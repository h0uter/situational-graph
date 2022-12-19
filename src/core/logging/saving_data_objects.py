import pickle
from datetime import datetime
import os


def load_something(name):
    full_path = os.path.join("saved_data", f"{name}.p")

    with open(full_path, "rb") as f:
        return pickle.load(f)


def save_something(obj, prefix=""):
    name = f"{prefix}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    full_path = os.path.join("saved_data", f"{name}.p")

    with open(full_path, "wb") as f:
        pickle.dump(obj, f)


if __name__ == "__main__":
    krm_stats = load_something("krm_stats_20220302-1654")
    print(krm_stats)
    krm_stats.plot_krm_stats()
