from __future__ import annotations

import json as _json
import urllib.error
import urllib.parse
import urllib.request


class Response:
    def __init__(self, status_code, headers, content, url):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.url = url

    @property
    def text(self):
        return self.content.decode("utf-8", errors="replace")

    def json(self):
        return _json.loads(self.text)

    def close(self):
        return None


def request(method, url, data=None, json=None, headers=None, timeout=10):
    body = None
    req_headers = dict(headers or {})

    if json is not None:
        body = _json.dumps(json).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    elif data is not None:
        if isinstance(data, dict):
            body = urllib.parse.urlencode(data).encode("utf-8")
        elif isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = data

    req = urllib.request.Request(url, data=body, headers=req_headers, method=method.upper())

    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            content = res.read()
            status_code = getattr(res, "status", res.getcode())
            res_headers = dict(res.headers.items())
    except urllib.error.HTTPError as e:
        content = e.read()
        status_code = e.code
        res_headers = dict(e.headers.items()) if e.headers else {}

    return Response(status_code=status_code, headers=res_headers, content=content, url=url)


def get(url, **kwargs):
    return request("GET", url, **kwargs)


def post(url, **kwargs):
    return request("POST", url, **kwargs)


def put(url, **kwargs):
    return request("PUT", url, **kwargs)


def delete(url, **kwargs):
    return request("DELETE", url, **kwargs)
