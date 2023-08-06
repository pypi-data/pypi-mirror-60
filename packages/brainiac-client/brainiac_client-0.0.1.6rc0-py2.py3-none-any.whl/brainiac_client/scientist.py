from io import BytesIO
from typing import Any, List, Optional
import pkg_resources
import json
import os
import urllib.parse
from brainiac_client.client import BRAINIAC_CLIENT_PASSWORD, BRAINIAC_CLIENT_USERNAME
from brainiac_client.constants import PICKLE_PROTOCOL
import cloudpickle
import requests


def login(url, username: Optional[str], password: Optional[str]) -> requests.Response:
    login_url = urllib.parse.urljoin(url, "/api/login")
    params = {'username': username, 'password': password}
    res = requests.post(url=login_url, json=params)
    return res


def get_installed_packages():
    installed_packages = pkg_resources.working_set
    return [i.key for i in installed_packages]


def package(some_class: Any,
            modelName: str,
            url: str = "http://libnosis.com",
            dependencies: List[str] = []) -> requests.Response:

    res = login(url, os.environ.get(BRAINIAC_CLIENT_USERNAME),
                os.environ.get(BRAINIAC_CLIENT_PASSWORD))
    cookies = res.headers.get("Set-Cookie")

    file = BytesIO(cloudpickle.dumps(some_class, protocol=PICKLE_PROTOCOL))

    files = {"pkledFile": file}
    data = {"modelName": modelName, "dependencies": json.dumps(dependencies)}
    url = urllib.parse.urljoin(url, "/api/model/upload")
    response = requests.put(url, files=files, data=data, headers={"Cookie": cookies})
    return response


__all__ = ["package"]
