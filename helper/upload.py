import requests


def upload_with_post(local_file, url):
    with open(local_file, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
        response.raise_for_status()

def upload_with_put(local_file, url ):
    with open(local_file, 'rb') as file:
        response = requests.put(url, data=file)
        response.raise_for_status()