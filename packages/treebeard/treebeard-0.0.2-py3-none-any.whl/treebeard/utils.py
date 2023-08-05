from google.cloud import storage
storage_client = storage.Client()
bucket_name = 'treebeard-notebook-outputs'


def save_artifact(name, path):
    blob = storage_client.bucket(bucket_name).blob(f'artifacts/{name}')
    blob.upload_from_filename(path)
