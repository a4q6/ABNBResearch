from pathlib import Path

assert Path(__file__).parent.joinpath("constants.py").exists(),\
    "No `constants.py` found. Please add `abn/common/constants.py` before using library."
