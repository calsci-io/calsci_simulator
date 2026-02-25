import json


class Response:
    def __init__(self, status_code=200, headers=None, content=b"", url=""):
        self.status_code = int(status_code)
        self.headers = headers or {}
        self.content = content
        self.url = url

    @property
    def text(self):
        try:
            return self.content.decode()
        except Exception:
            return ""

    def json(self):
        if not self.content:
            return {}
        try:
            return json.loads(self.text)
        except Exception:
            return {}

    def close(self):
        return None


def _offline_payload(url):
    if "check-pending-apps" in url:
        return 200, {"response": "none"}

    if "get-pending-apps" in url:
        payload = {
            "response": {
                "app_name": "",
                "app_folder": "installed_apps",
                "code": "",
            },
            "app_name": "",
            "app_folder": "installed_apps",
            "code": "",
        }
        return 200, payload

    if "confirm-download" in url:
        return 200, {"response": "skipped"}

    return 503, {"response": "offline"}


def request(method, url, data=None, json=None, headers=None, timeout=10):
    _ = (method, data, json, headers, timeout)

    status, payload = _offline_payload(url)
    content = bytes(json_module_dumps(payload), "utf-8")
    return Response(status_code=status, headers={"content-type": "application/json"}, content=content, url=url)


def json_module_dumps(obj):
    try:
        return json.dumps(obj)
    except Exception:
        return "{}"


def get(url, **kwargs):
    return request("GET", url, **kwargs)


def post(url, **kwargs):
    return request("POST", url, **kwargs)


def put(url, **kwargs):
    return request("PUT", url, **kwargs)


def delete(url, **kwargs):
    return request("DELETE", url, **kwargs)
