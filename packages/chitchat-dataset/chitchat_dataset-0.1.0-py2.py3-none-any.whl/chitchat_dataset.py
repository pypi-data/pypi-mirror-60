"""Chit Chat Challenge dataset."""

__version__ = "0.1.0"

import json
import os


class Dataset(dict):
    """Chit Chat Challenge dataset."""

    def __init__(self, path=None):
        if path is None:
            parent = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            path = os.path.join(parent, "dataset.json")
        self.path = path
        super(Dataset, self).__init__(json.load(open(self.path)))
