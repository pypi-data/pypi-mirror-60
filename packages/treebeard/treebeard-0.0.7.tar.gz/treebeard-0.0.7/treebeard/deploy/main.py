from google.cloud import storage
import papermill as pm
import os

storage_client = storage.Client()
bucket_name = 'treebeard-notebook-outputs'

if __name__ == '__main__':
    blob = storage_client.bucket(bucket_name).blob('out.ipynb')

    pm.execute_notebook('./main.ipynb',
                        '/tmp/out.ipynb', progress_bar=False)

    blob.upload_from_filename('/tmp/out.ipynb')
