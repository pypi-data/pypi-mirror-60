from pathlib import Path
import os


def get_notebook_name():
    if not os.path.isfile(f"{os.getcwd()}/main.ipynb"):
        raise Exception(
            "The current directory must contain a file named main.ipynb")
    return Path(os.getcwd()).name


def get_treebeard_env():
    treebeard_project_id = os.getenv('TREEBEARD_PROJECT_ID')
    run_id = os.getenv('TREEBEARD_RUN_ID')

    treebeard_env = {
        'notebook_id': get_notebook_name(),
        'project_id': treebeard_project_id,
        'run_id': run_id
    }

    return treebeard_env


def get_run_path():
    treebeard_env = get_treebeard_env()
    print(f"Treebeard env is {treebeard_env}")
    return f"{treebeard_env['project_id']}/{treebeard_env['notebook_id']}/{treebeard_env['run_id']}"
