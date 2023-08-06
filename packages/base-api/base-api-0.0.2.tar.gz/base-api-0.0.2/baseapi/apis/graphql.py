import requests

from ..exceptions import QueryException
from ..utils import FileID, remove_trailing_slash

from .api import Api


class GraphqlApi(Api):
    def perform_query(self, query, variables=None, headers=None):
        response = self.send_query(query, variables, headers)
        response_data = response.json()
        self.check_for_errors(response_data)
        return response_data['data']

    def send_query(self, query, variables, headers):
        url = remove_trailing_slash(self.client.url)
        url = f'{url}/graphql/'
        auth_headers = {}
        if self.client.jwt:
            auth_headers['Authorization'] = f'Bearer {self.client.jwt}'
        response = requests.post(
            url,
            json={
                'query': query,
                'variables': variables
            },
            headers={
                **auth_headers,
                **(headers or {})
            }
        )
        if response.status_code not in self.SUCCESS_RESPONSE_CODES:
            msg = response.content
            raise QueryException(f'API error: {msg}')
        return response

    def check_for_errors(self, response_data):
        # GraphQL responses only throw 400s and 500s if something goes
        # very wrong, so we need to check the error fields in addition.
        if response_data.get('errors'):
            try:
                msg = response_data['errors'][0]['message']
            except Exception:
                msg = 'unknown reason'
            raise QueryException(f'API error: {msg}')

    def make_variables(self, **kwargs):
        return {
            key: value
            for key, value in kwargs.items()
            if value is not None
        }

    def check_file_id(self, file_id):
        if file_id is not None:
            if not isinstance(file_id, FileID):
                raise TypeError('File uploads must be FileID objects')
            file_id = str(file_id)
        return file_id
