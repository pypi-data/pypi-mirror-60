from pathlib import Path
import os


def get_notebook_name():
    if not os.path.isfile(f"{os.getcwd()}/main.ipynb"):
        raise Exception(
            "The current directory must contain a file named main.ipynb")
    return Path(os.getcwd()).name
