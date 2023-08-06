from pathlib import Path
import click
import os
import configparser


def get_notebook_name():
    if not os.path.isfile(f"{os.getcwd()}/main.ipynb"):
        raise Exception(
            "The current directory must contain a file named main.ipynb")
    return Path(os.getcwd()).name


def get_treebeard_env():
    """Reads variables from a local file, credentials.cfg"""
    config = configparser.RawConfigParser()
    treebeard_project_id = ''
    run_id = ''
    email = ''
    api_key = ''

    try:
        config.read('credentials.cfg')
        treebeard_project_id = config.get(
            'credentials', 'TREEBEARD_PROJECT_ID')
        email = config.get('credentials', 'TREEBEARD_EMAIL')
        api_key = config.get('credentials', 'TREEBEARD_API_KEY')
        # run_id = config.get('credentials', 'TREEBEARD_RUN_ID')

        run_id = os.getenv('TREEBEARD_RUN_ID')
        # treebeard_project_id = os.getenv('TREEBEARD_PROJECT_ID')
        # email = os.getenv('TREEBEARD_EMAIL')
        # api_key = os.getenv('TREEBEARD_API_KEY')
        if not api_key:
            click.echo(click.style(
                'Warning! No API key found \nTreebeard may behave unexpectedly \nPlease email alex@treebeard.io to obtain an API key then run `treebeard configure`', fg='red'))
    except:
        click.echo(click.style(
            "No credentials file found. Please run `treebeard configure`", fg='red'))

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
