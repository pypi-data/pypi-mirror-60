from dataclasses import asdict
from typing import List, Optional, Tuple, Union

from .exceptions import DirectusException
from .models import Collection
from .utils import ApiClient


class DirectusClient:
    """
    DirectusClient provide a way to interact with Directus API on a defined server.
    It eases the use of [Directus API](https://docs.directus.io/api/reference.html) by providing
    simple methods to access to the resources.

    Attributes
    ----------
    url: str
        The url of the Directus server you want to connect to

    email: str
        The email account you want to use to connect to the Directus server

    password: str
        The associated password corresponding to the email account

    project: str
        The name of the project you want to access on the specified server. If no project 
        name is provided, default is "_" (default project in Directus)
    """

    def __init__(self, url: Optional[str] = None, email: Optional[str] = None,
                 password: Optional[str] = None, project: str = "_"):
        if not url:
            raise DirectusException("You must provide a server url")

        if not email:
            raise DirectusException("You must provide an email")

        if not password:
            raise DirectusException("You must provide a password")

        if not project:
            raise DirectusException("You must provide a project")

        self.ApiClient = ApiClient(
            url=url, email=email, password=password, project=project)

    '''

    Collections
    https://docs.directus.io/api/collections.html

    '''

    def get_collections_list(self, offset: int = 0, single: bool = False,
                             meta: List[str] = []) -> Tuple[Union[Collection, List[Collection]], dict]:
        """
        Find out more: https://docs.directus.io/api/collections.html#list-collections

        Returns
        -------
            (List of Collection, metadata)
        """
        path = "collections"
        params = {
            "offset": offset,
            "single": int(single)
        }
        response_data, response_meta = self.ApiClient.do_get(
            path=path, params=params, meta=meta)

        if params.get('single') and params['single']:
            return Collection(**response_data), response_meta

        return [Collection(**collection) for collection in response_data], response_meta

    def get_collection(self, collection_name: str, meta: List[str] = []) -> Tuple[Collection, dict]:
        """
        Find out more: https://docs.directus.io/api/collections.html#retrieve-a-collection

        Returns
        -------
            (Collection, metadata)
        """
        path = "/".join(["collections", collection_name])
        response_data, response_meta = self.ApiClient.do_get(
            path=path, meta=meta)

        return Collection(**response_data), response_meta

    def create_collection(self, new_collection: Collection, meta: List[str] = []) -> Tuple[Collection, dict]:
        """
        Find out more: https://docs.directus.io/api/collections.html#create-a-collection

        Returns
        -------
            (Collection, metadata)
        """
        path = "collections"
        response_data, response_meta = self.ApiClient.do_post(
            path=path, data=asdict(new_collection), meta=meta)

        return Collection(**response_data), response_meta

    def update_collection(self, collection_name: str, data: dict,
                          meta: List[str] = []) -> Tuple[Collection, dict]:
        """
        Find out more: https://docs.directus.io/api/collections.html#update-a-collection

        Returns
        -------
            (Collection, metadata)
        """
        path = "collections"
        response_data, response_meta = self.ApiClient.do_patch(
            path=path, id=collection_name, data=data, meta=meta)

        return Collection(**response_data), response_meta

    def delete_collection(self, collection_name: str) -> bool:
        """
        Find out more: https://docs.directus.io/api/collections.html#delete-a-collection

        Returns
        -------
            bool (True if deleted, False if not)
        """
        path = "collections"
        is_deleted = self.ApiClient.do_delete(path=path, id=collection_name)

        return is_deleted

    '''

    Items
    https://docs.directus.io/api/items.html

    '''

    def get_items_list(self, collection_name: str, fields: List[str] = ['*'], page: Optional[int] = None, limit: int = 100,
                       offset: int = 0, sort: List[str] = ['id'], single: bool = False, filter: dict = {},
                       status: Optional[str] = None, q: Optional[str] = None, meta: List[str] = []) -> Tuple[Union[dict, List[dict]], dict]:
        """
        Find out more: https://docs.directus.io/api/items.html#list-the-items

        Returns
        -------
            (List of item, metadata)
        """
        path = "/".join(["items", collection_name])

        params = {
            'fields': ",".join(fields),
            'limit': limit,
            'offset': offset,
            'sort': ",".join(sort),
            'single': single,
            'filter': filter,
            'status': status,
            'q': q
        }

        if page:
            params['page'] = page
            del params['offset']

        response_data, response_meta = self.ApiClient.do_get(
            path, params=params, meta=meta)

        return response_data, response_meta

    def get_all_items_list(self, collection_name: str, fields: List[str] = ['*'],
                           sort: List[str] = ['id'], filter: dict = {}, status: Optional[str] = None, q: Optional[str] = None,
                           meta: List[str] = [], page: int = 1) -> Tuple[List[dict], dict]:
        """
        Find out more: https://docs.directus.io/api/items.html#list-the-items

        Returns
        -------
            (List of item, metadata)
        """
        path = "/".join(["items", collection_name])

        if 'page' not in meta:
            meta.append('page')

        response_data, response_meta = self.get_items_list(
            collection_name=collection_name, fields=fields, sort=sort, filter=filter, page=page, status=status, q=q, meta=meta)

        if int(response_meta['page']) < int(response_meta['page_count']):
            next_page = int(response_meta['page']) + 1
            recursive_data, _ = self.get_all_items_list(
                collection_name=collection_name, fields=fields, page=next_page, sort=sort, filter=filter, status=status, q=q, meta=meta)
            response_data += recursive_data

        return response_data, response_meta

    def get_item(self, collection_name: str, id: int, fields: List[str] = ['*'], meta: List[str] = []) -> Tuple[dict, dict]:
        """
        Find out more: https://docs.directus.io/api/items.html#retrieve-an-item

        Returns
        -------
            (item, metadata)
        """
        path = "/".join(['items', collection_name, str(id)])
        params = {
            'fields': ",".join(fields)
        }

        return self.ApiClient.do_get(
            path=path, params=params, meta=meta)

    def create_item(self, collection_name: str, item: dict, meta: List[str] = []) -> Tuple[dict, dict]:
        """
        Find out more: https://docs.directus.io/api/items.html#create-an-item

        Returns
        -------
            (item, metadata)
        """
        path = "/".join(['items', collection_name])

        return self.ApiClient.do_post(path=path, data=item, meta=meta)

    def update_item(self, collection_name: str, id: int, data: dict, fields: List[str] = ['*'], meta: List[str] = []) -> Tuple[dict, dict]:
        """
        Find out more: https://docs.directus.io/api/items.html#update-an-item

        Returns
        -------
            (item, metadata)
        """
        path = "/".join(['items', collection_name, str(id)])

        return self.ApiClient.do_patch(path=path, id=id, data=data, meta=meta)

    def delete_item(self, collection_name: str, id: int) -> bool:
        """
        Find out more: https://docs.directus.io/api/items.html#delete-an-item

        Returns
        -------
            bool (True if deleted, False if not)
        """
        path = "/".join(['items', collection_name])

        return self.ApiClient.do_delete(path=path, id=id)
    # def getItemRevisions(self, collection: str, id: int, fields: List[str] = ['*'], limit: int= 100, offset: int = 0)

    '''

    Files
    https://docs.directus.io/api/files.html

    '''

    def get_files_list(self, fields: List[str] = ['*'], limit: int = 100,
                       offset: int = 0, sort: List[str] = ['id'], single: bool = False, filter: dict = {},
                       status: Optional[str] = None, q: Optional[str] = None, meta: List[str] = []) -> Tuple[Union[dict, List[dict]], dict]:
        """
        Find out more: https://docs.directus.io/api/files.html#list-the-files

        Returns
        -------
            (List of file, metadata)
        """
        path = "/".join(["files"])

        params = {
            'fields': ",".join(fields),
            'limit': limit,
            'offset': offset,
            'sort': ",".join(sort),
            'single': single,
            'filter': filter,
            'status': status,
            'q': q
        }

        response_data, response_meta = self.ApiClient.do_get(
            path, params=params, meta=meta)

        return response_data, response_meta

    def get_file(self, id: int, fields: List[str] = ['*'], meta: List[str] = []) -> Tuple[dict, dict]:
        """
        Find out more: https://docs.directus.io/api/files.html#retrieve-a-file

        Returns
        -------
            (file, metadata)
        """
        path = "/".join(['files', str(id)])
        params = {
            'fields': ",".join(fields)
        }

        return self.ApiClient.do_get(
            path=path, params=params, meta=meta)
