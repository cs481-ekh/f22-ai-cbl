from pathlib import Path
import os


root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent

raw_data_dir = Path.joinpath(root_dir, "data", "raw")
processed_data_dir = Path.joinpath(root_dir, "data", "processed")
cleaned_data_dir = Path.joinpath(root_dir, "data", "cleaned")
