import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Union


class FileHandler:
    def __init__(self, filepath: str):
        self.BASE_DIR = Path(filepath).resolve().parent

    @staticmethod
    def time_string():
        return datetime.utcnow().strftime("%Y-%m-%d_%H%M%S%F_UTC")

    def read_file(self, path: str):
        with open(self.BASE_DIR / path, "r") as f_in:
            return f_in.read()

    def to_file(self, path: str, data: Union[str, dict], default: Callable = None):
        with open(self.BASE_DIR / path, "w") as f_out:
            if isinstance(data, (dict, list)):
                data = json.dumps(data, indent=4)
            f_out.write(data)

    def json_to_dict(self, path: str):
        with open(self.BASE_DIR / path) as f_in:
            return json.load(f_in)

    def to_json(self, path: str, data: Union[list, dict], default: Callable = None):
        with open(self.BASE_DIR / path, "w") as f_out:
            json.dump(
                data, f_out, indent=4, default=default if default else lambda o: str(o)
            )
