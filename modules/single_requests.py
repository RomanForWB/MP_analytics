import requests

session = None


def init_connection(new=True):
    global session
    if session is not None and new == False: return
    elif session is not None and new == True:
        session.close()
        session = requests.Session()
    else: session = requests.Session()


def fetch(http_method, content_type='text', url=None, body=None,
          params=None, headers=None, timeout=10):
    global session
    init_connection()
    while True:
        try:
            if http_method.lower() == 'get':
                response = session.get(url=url, headers=headers, params=params, timeout=timeout)
            elif http_method.lower() == 'post':
                response = session.post(url=url, headers=headers, params=params, json=body, timeout=timeout)
            if 300 > response.status_code >= 200:
                if content_type.lower() == 'json': result = response.json()
                else: result = response.text
                return result
        except (requests.exceptions.RequestException, requests.exceptions.BaseHTTPError):
            init_connection(new=True)
            timeout += 5
