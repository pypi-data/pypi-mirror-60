from json import JSONDecodeError
from typing import List, Optional, Tuple, Union
from urllib.parse import urljoin

from requests import Response, request

from ..exceptions import DirectusException


class ApiClient(object):

    def __init__(self, url: str, project: str, email: Optional[str] = None, password: Optional[str] = None):
        self.baseHeader = {}
        self.url = url
        self.baseUrl = urljoin(url, project)
        self.project = project
        if email is not None and password is not None:
            auth, _ = self.do_post(
                path="auth/authenticate", data={"email": email, "password": password})
            self.baseHeader['authorization'] = f"Bearer {auth['token']}"

    def do_get(self, path: str, params: dict = {}, headers: dict = {}, meta: List[str] = []) -> Tuple[dict, dict]:
        headers = {**self.baseHeader, **headers}
        params['meta'] = ",".join(meta)
        response = self._make_request(
            'GET', "/".join([self.baseUrl, path]), headers=headers, params=params)
        result = response.json()

        return result['data'], result['meta'] if result.get('meta') else {}

    def do_post(self, path: str, data: dict, headers: dict = {}, meta: List[str] = []) -> Tuple[dict, dict]:
        headers = {**self.baseHeader, **headers}
        params = {"meta": meta}
        response = self._make_request(
            'POST', "/".join([self.baseUrl, path]), headers=headers, data=data, params=params)
        result = response.json()

        return result['data'], result['meta'] if result.get('meta') else {}

    def do_patch(self, path: str, id: Union[str, int], data: dict, headers: dict = {}, meta: List[str] = []) -> Tuple[dict, dict]:
        headers = {**self.baseHeader, **headers}
        params = {"meta": meta}
        url = "/".join([self.baseUrl, path, str(id)])
        response = self._make_request(
            'PATCH', url, headers=headers, data=data, params=params)
        result = response.json()

        return result['data'], result['meta'] if result.get('meta') else {}

    def do_delete(self, path: str, id: Union[int, str], headers: dict = {}) -> bool:
        headers = {**self.baseHeader, **headers}
        url = "/".join([self.baseUrl, path, str(id)])
        response = self._make_request('DELETE', url, headers=headers)

        if response.status_code != 204:
            return False

        return True

    def _make_request(self, method: str, url: str, headers: dict, data: dict = {}, params: dict = {}) -> Response:
        response = request(method=method, url=url,
                           headers=headers, json=data, params=params)

        try:
            if response.json().get("error"):
                raise DirectusException(
                    f"{response.json()['error']['message']} ( Code {response.json()['error']['code']}: Please have a look at https://docs.directus.io/api/errors.html )")
        except JSONDecodeError:
            pass
            # log empty response

        return response
