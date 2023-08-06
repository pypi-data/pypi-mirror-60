from google.cloud import storage
import papermill as pm
import os
from flask import Flask, request
app = Flask(__name__)

storage_client = storage.Client()
bucket_name = 'treebeard-notebook-outputs'
# try:
# storage_client.create_bucket(bucket_name)
# except:
#     pass


def helloPubSub(event, context):
    blob = storage_client.bucket(bucket_name).blob('out.ipynb')

    pm.execute_notebook('./main.ipynb',
                        '/tmp/out.ipynb', progress_bar=False)

    blob.upload_from_filename('/tmp/out.ipynb')


@app.route('/', methods=['POST'])
def index():
    envelope = request.get_json()
    helloPubSub(None, None)
    return ('', 200)


if __name__ == '__main__':

    helloPubSub(None, None)
