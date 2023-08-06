from pathlib import Path
import click
import os


def get_notebook_name():
    if not os.path.isfile(f"{os.getcwd()}/main.ipynb"):
        raise Exception(
            "The current directory must contain a file named main.ipynb")
    return Path(os.getcwd()).name


def get_treebeard_env():
    click.echo('get_treebeard_env')
    treebeard_project_id = os.getenv('TREEBEARD_PROJECT_ID')
    run_id = os.getenv('TREEBEARD_RUN_ID')
    email = os.getenv('TREEBEARD_EMAIL')
    api_key = os.getenv('TREEBEARD_API_KEY')
    if not api_key:
        click.echo(click.style(
            'Warning! No API key found \nTreebeard may behave unexpectedly \nPlease email alex@treebeard.io to obtain an API key then run treebeard configure', fg='red'))

    treebeard_env = {
        'notebook_id': get_notebook_name(),
        'project_id': treebeard_project_id,
        'run_id': run_id,
        'email': email,
        'api_key': api_key
    }

    return treebeard_env


def get_run_path():
    treebeard_env = get_treebeard_env()
    print(f"Treebeard env is {treebeard_env}")
    return f"{treebeard_env['project_id']}/{treebeard_env['notebook_id']}/{treebeard_env['run_id']}"
