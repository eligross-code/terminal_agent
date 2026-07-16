# local_stats.py

import json
from pathlib import Path


STATE_PATH = Path(__file__).with_name("local_stats.json")

DEFAULT_STATE = {
    "total_tokens_generated": 0,
    "total_tokens_input": 0,
    "num_calls": 0,
}


def load_local_state():
    if not STATE_PATH.exists():
        return DEFAULT_STATE.copy()

    with open(STATE_PATH, "r") as file:
        return json.load(file)


local_state = load_local_state()


def save_local_state():
    with open(STATE_PATH, "w") as file:
        json.dump(local_state, file, indent=4)


def access_local_state():
    return local_state.copy()