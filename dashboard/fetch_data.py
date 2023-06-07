import requests
import json
from .models import WikiData


def fetch_data(keyword):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{keyword}"
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    title = data['title']
    content = data['extract']
    return title, content


def read_keywords(file_path):
    with open(file_path, 'r') as f:
        keywords = f.read().splitlines()
    return keywords



def store_data(title, content):
    wiki_data = WikiData.objects.create(title=title, content=content)
    return wiki_data

