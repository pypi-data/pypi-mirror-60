#! python
import click

from google.cloud import storage
from google.cloud import scheduler
import shutil
from halo import Halo
import time
import os
import subprocess
# Instantiates a client
dir_path = os.path.dirname(os.path.realpath(__file__))

storage_client = storage.Client()

# The name for the new bucket
bucket_name = "new_bucket_for_treebeard"

bucket = storage_client.get_bucket(bucket_name)


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


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command()
def init():
    click.echo('Synching')


def get_time_secs():
    return int(time.time())


@cli.command()
def schedule():
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

    subprocess.run([f'{dir_path}/treebeard', 'schedule'])


@cli.command()
def list():
    subprocess.run([f'{dir_path}/treebeard', 'list'])


@cli.command()
def run():
    subprocess.run([f'{dir_path}/treebeard', 'run'])


if __name__ == '__main__':
    cli()
