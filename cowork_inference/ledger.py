"""Read the local snapshot. This package does not call Graph, Azure, or Cowork."""

import json
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).with_name("snapshot.json")


def load_snapshot():
    with SNAPSHOT_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def teams():
    return list(load_snapshot()["teams"])
