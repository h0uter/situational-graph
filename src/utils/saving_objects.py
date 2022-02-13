import pickle
import os
import time


def load_something(name):
    full_path = os.path.join('saved_data', f'{name}.p')
    # full_path = os.path.join('saved_data', f'{time.time()}_{name}.p')
    with open(full_path, 'rb') as f:
        return pickle.load(f)


def save_something(obj, name):
    full_path = os.path.join('saved_data', f'{name}.p')
    # full_path = os.path.join('saved_data', f'{time.time()}_{name}.p')
    with open(full_path, 'wb') as f:
        pickle.dump(obj, f)