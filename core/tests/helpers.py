import requests


def create_response(status_code=200, json_body={}):
    response = requests.Response()
    response.status_code = status_code
    response.json = lambda: json_body
    return response
