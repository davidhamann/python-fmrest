import json

import requests
from typing import Dict, Any, Optional, Tuple, List

from . import Server
from .exceptions import BadJSON
from .foundset import Foundset
from .record import Record
from .utils import request_async

try:
    import aiohttp
except ImportError as e:
    raise ValueError("Install aiohttp")


class ServerAsync(Server):
    def __repr__(self) -> str:
        return '<ServerAsync logged_in={} database={} layout={}>'.format(
            bool(self._token), self.database, self.layout
        )

    async def create_record_async(self,
                                 field_data: Dict[str, Any],
                                 portals: Optional[Dict[str, Any]] = None,
                                 scripts: Optional[Dict[str, List]] = None) -> Optional[int]:
        payload = self.create_record_prepare_payload(field_data, portals, scripts)
        response = await self._call_filemaker_async(**payload)
        return self.create_record_prepare_result(response)

    @Server._with_auto_relogin
    async def edit_record_async(self,
                                record_id: int,
                                field_data: Dict[str, Any],
                                mod_id: Optional[int] = None,
                                portals: Optional[Dict[str, Any]] = None,
                                scripts: Optional[Dict[str, List]] = None) -> bool:
        payload = self.edit_record_prepare_payload(record_id,
                                                   field_data,
                                                   mod_id,
                                                   portals,
                                                   scripts)
        await self._call_filemaker_async(**payload)
        return self.edit_record_prepare_result()

    @Server._with_auto_relogin
    async def delete_record_async(self, record_id: int, scripts: Optional[Dict[str, List]] = None):
        payload = self.delete_record_prepare_payload(record_id,
                                                     scripts)
        await self._call_filemaker_async(**payload)
        return self.delete_record_prepare_response()

    @Server._with_auto_relogin
    async def get_record_async(self, record_id: int,
                               portals: Optional[List[Dict]] = None,
                               scripts: Optional[Dict[str, List]] = None,
                               layout: Optional[str] = None) -> Record:
        payload = self.get_record_prepare_payload(record_id,
                                                  portals,
                                                  scripts,
                                                  layout)
        response = await self._call_filemaker_async(**payload)
        return self.get_record_prepare_result(response)

    @Server._with_auto_relogin
    async def perform_script_async(self, name: str, param: Optional[str] = None) -> Tuple[Optional[int], Optional[str]]:
        payload = self.perform_script_prepare_payload(name, param)
        response = await self._call_filemaker_async(**payload)
        return self.perform_script_prepare_result(response)

    @Server._with_auto_relogin
    async def get_records_async(self,
                                offset: int = 1,
                                limit: int = 100,
                                sort: Optional[List[Dict[str, str]]] = None,
                                portals: Optional[List[Dict[str, Any]]] = None,
                                scripts: Optional[Dict[str, List]] = None,
                                layout: Optional[str] = None) -> Foundset:
        payload = self.get_records_prepare_payload(offset,
                                                   limit,
                                                   sort,
                                                   portals,
                                                   scripts,
                                                   layout)
        response = await self._call_filemaker_async(**payload)
        return self.get_records_prepare_result(response)

    @Server._with_auto_relogin
    async def find_async(self,
                         query: List[Dict[str, Any]],
                         sort: Optional[List[Dict[str, str]]] = None,
                         offset: int = 1,
                         limit: int = 100,
                         portals: Optional[List[Dict[str, Any]]] = None,
                         scripts: Optional[Dict[str, List]] = None,
                         layout: Optional[str] = None) -> Foundset:
        payload = self.find_prepare_payload(query,
                                            sort,
                                            offset,
                                            limit,
                                            portals,
                                            scripts,
                                            layout)
        response = await self._call_filemaker_async(**payload)
        return self.find_prepare_result(response)

    @Server._with_auto_relogin
    async def fetch_file_async(self,
                               file_url: str,
                               stream: bool = False) -> Tuple[str,
                                                        Optional[str],
                                                        Optional[str],
                                                        requests.Response]:
        payload = self.fetch_file_prepare_payload(file_url,
                                                  stream)
        response = await self._call_filemaker_async(**payload)
        return self.fetch_file_prepare_result(file_url, response)

    @Server._with_auto_relogin
    async def set_globals_async(self, globals_: Dict[str, Any]) -> bool:
        payload = self.set_globals(globals_)
        await self._call_filemaker_async(**payload)
        return self.set_globals_prepare_result()

    @Server._with_auto_relogin
    async def _call_filemaker_async(self, method: str, path: str,
                                    data: Optional[Dict] = None,
                                    params: Optional[Dict] = None,
                                    **kwargs: Any) -> Dict:
        url = self.url + path
        # if we have a token, make sure it's included in the header
        # if not, the Authorization header gets removed (necessary for example for logout)
        self._update_token_header()
        response_text = await request_async(method,
                                            path=url,
                                            json=data,
                                            params=params,
                                            headers=self._headers,
                                            verify_ssl=self.verify_ssl,
                                            **kwargs)

        try:
            response_data = json.loads(response_text)
        except json.decoder.JSONDecodeError as ex:
            raise BadJSON(ex, response_text) from None

        return self.handle_response_data(response_data)
