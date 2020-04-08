from argparse import Namespace
import json


def read_json_config_file(path):
    with open(path) as fp:
        cfg = json.load(fp)
        cfg_ns = Namespace(**cfg)

        return cfg_ns
