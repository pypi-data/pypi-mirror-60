#! python
import warnings
import click
import shutil
import time
import os
import base64
import tarfile
import json
import os.path
import subprocess
import secrets
import configparser
import requests
# from Firebase import auth
from google.cloud import storage
from google.cloud import scheduler
from halo import Halo
from treebeard.utils import list_artifacts

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials")

# Instantiates a client
dir_path = os.path.dirname(os.path.realpath(__file__))
storage_client = storage.Client()
# bucket_name = "new_bucket_for_treebeard"
bucket_name = 'treebeard-notebook-outputs'
bucket = storage_client.get_bucket(bucket_name)


def set_credentials(email):
    """Create user credentials"""
    key = secrets.token_urlsafe(16)
    config = configparser.RawConfigParser()
    config = configparser.RawConfigParser()
    config.add_section('credentials')
    config.set('credentials', 'TREEBEARD_API_KEY', key)
    config.set('credentials', 'TREEBEARD_EMAIL', email)
    with open('credentials.cfg', 'w') as configfile:
        config.write(configfile)
    os.environ["TREEBEARD_API_KEY"] = key
    os.environ["TREEBEARD_EMAIL"] = email
    click.echo(f'User credentials saved. Email: {email}, API key: {key}')
    return key, email

# Scheduler gives token
# Scheduler takes token and resolves with user ID and knows it is the person


def fetch_credentials():
    """
    Checks for user credentials and returns user email and API key
    """
    # Does credentials.cfg exist and if it does, can we read the API key
    config = configparser.RawConfigParser()
    creds_path = 'credentials.cfg'
    try:
        os.path.isfile(creds_path)
        config.read(creds_path)
        key = config.get('credentials', 'TREEBEARD_API_KEY')
        email = config.get('credentials', 'TREEBEARD_EMAIL')
        click.echo('Connecting to your account.')
    except:
        click.echo(f"No credentials found - please run: treebeard configure")
    return key, email


def firebase_auth(key, email):
    """Login or create account in a webpage"""
    # additional_claims = {
    #     'email': 'myemail@me.com'
    # }
    # custom_token = auth.create_custom_token('myapikey', additional_claims)

    # click.launch(
    #     f'https://treebeard.io/app/login?email={email}&key=&{key}')
    click.echo('Webpage launch')
    return


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command()
@click.option('--email', prompt='Your email:')
def configure(email):
    """ Set initial credentials"""
    set_credentials(email)


@cli.command()
def init():
    """Connect to Treebeard account (browser popup or CLI login)
    """
    # Check if local credentials exist
    key, email = fetch_credentials()
    # Authorise User Account with Firebase
    firebase_auth(key, email)
    click.echo(f'Account initialised for {email}, key: {key}')
    return


@cli.command()
def list():
    """Lists all deployed filenames"""
    click.echo(f'Listing deployed filenames:')
    subprocess.run([f'{dir_path}/treebeard', 'list'])


@cli.command()
@click.argument('filename', type=click.Path(exists=True))
def deploy(filename):
    """Deploy a notebook to the cloud"""
    click.echo(f'Deploying notebook {filename} to the cloud.')
    click.secho(f'Notebook {filename} deployed successfully.', fg='green')


@cli.command()
@click.option('--file', '-f', 'filename', default=None, type=click.Path(exists=True), help='Outputs of deployed files.')
def outputs(filename):
    """ View URLs for notebook outputs to be served or accessed."""
    if filename:
        click.echo(f'Outputs for notebook {filename}:')
    else:
        click.echo('Outputs for all notebooks:')
        list_artifacts(bucket_name)


@cli.command()
@click.option('--file', '-f', 'filename', default=None, type=click.Path(exists=True),
              help='Specify notebook to see logs')
def logs(filename):
    """
    See all actions and deployment results
    """
    if filename:
        click.echo(f'Historical deployments for {filename}:')
    else:
        click.echo('Historical deployments for all notebooks:')


@cli.command()
@click.argument('dirname', type=click.Path(exists=True))
@click.option('t', '--hourly', flag_value='hourly', help='Run notebook hourly')
@click.option('t', '--daily', default=True, flag_value='daily', help='Run notebook daily')
@click.option('t', '--weekly', flag_value='weekly', help='Run notebook weekly')
@click.option('t', '--monthly', flag_value='monthly', help='Run notebook monthly')
def schedule(dirname, t):
    """
    Schedule a notebook to run periodically
    """

    print("Compressing project")
    archive_filename = '/tmp/treebeard_upload.tgz'
    with tarfile.open(archive_filename, "w:gz") as tar:
        tar.add(dirname, arcname=os.path.basename(os.path.sep))

    endpoint = 'http://localhost:8080/build'
    endpoint = 'https://scheduler-cvee2224cq-ew.a.run.app/build'
    # print("Submitting Request")
    response = requests.post(
        endpoint, files={'repo': open('/tmp/treebeard_upload.tgz', 'rb')})

    print(response.status_code)
# def deploy_notebook(notebook):
# blob = bucket.blob('uploaded_notebook.ipynb')
# blob.upload_from_filename(notebook)
# client = scheduler.CloudSchedulerClient()
# parent = client.location_path('treebeard-259315', 'europe-west1')
# try:
#     client.delete_job(
#         'projects/treebeard-259315/locations/europe-west1/jobs/treebeard-job')
# except:
#     pass

# client.create_job(parent, {
#                   "name": 'projects/treebeard-259315/locations/europe-west1/jobs/treebeard-job',
#                   "attempt_deadline": "180s",
#                   "http_target": {
#                       "headers": {
#                           "User-Agent": "Google-Cloud-Scheduler"
#                       },
#                       "http_method": "POST",
#                       "uri": "https://example-cvee2224cq-ew.a.run.app/"
#                   },
#                   "schedule": '* * * * *'})

# @cli.command()
# def schedule():
    # zip_location = '.treebeard_archive'
    # archive_format = 'zip'
    # shutil.make_archive(zip_location, archive_format, '.')
    # upload_blob = bucket.blob('uploaded_package')
    # upload_blob.upload_from_filename(zip_location + '.' + archive_format)

    # spinner = Halo(text='Loading', spinner='dots')
    # spinner.start()

    # log_blob = bucket.blob('log')
    # timeout = 30
    # start_time = get_time_secs()
    # timed_out = False

    # subprocess.run('./deploy.sh')

    # while not log_blob.exists():
    #     if get_time_secs() - start_time > timeout:
    #         timed_out = True
    #         break
    #     time.sleep(2)

    # if timed_out:
    #     spinner.stop()
    #     click.echo('Failed to set schedule (No submission logs found).')
    #     return

    # log_blob.download_as_string()
    # spinner.stop()

    # subprocess.run([f'{dir_path}/treebeard', 'schedule'])
