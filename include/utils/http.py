
import requests

def get(url):
    response = requests.get(url)
    return response.text
