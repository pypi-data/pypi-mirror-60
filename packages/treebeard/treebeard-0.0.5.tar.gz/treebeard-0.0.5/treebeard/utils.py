import os
import warnings
from google.cloud import storage
import gcsfs
import pandas as pd
fs = gcsfs.GCSFileSystem(project="treebeard-259315")

storage_client = storage.Client()
bucket_name = 'treebeard-notebook-outputs'

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials")


def list():
    fs.ls(bucket_name)


def download(file_name, bucket_name=bucket_name):
    fs.get(f'{bucket_name}/{file_name}', f'{file_name}')


def read_csv(file_name, bucket_name=bucket_name):
    with fs.open(f'{bucket_name}/{file_name}') as f:
        return pd.read_csv(f)


def list_files():
    pass


def save_to_cloud():
    pass


def list_artifacts():
    pass
