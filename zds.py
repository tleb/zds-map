import requests


class Zds:
    base_uri = 'https://zestedesavoir.com'

    def __init__(self, client_id, client_secret, refresh_token_path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token_path = refresh_token_path

        self._refresh_token = None
        self.access_token = ''

    def _request(self, uri_path, method='GET', body=None, returned_unauthorized=False):
        # TODO: add infos to the errors' messages
        if not self.access_token:
            self._refresh_access_token()

        uri = self.base_uri + uri_path
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}

        res = requests.request(method, uri, headers=headers, json=body)

        if res.status_code == 401:
            if returned_unauthorized:
                raise RuntimeError('Two 401 in a row')
            self._refresh_access_token()
            return self._request(uri_path, method, body, True)
        elif res.status_code != 200:
            raise RuntimeError('ZdS answered with an unexpected status code')

        return res

    def _refresh_access_token(self):
        uri = '{}/oauth2/token/'.format(self.base_uri)

        data = {'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token}

        res = requests.post(uri, json=data)

        self.access_token = res.access_token
        self.refresh_token = res.refresh_token

    @property
    def refresh_token(self):
        if self._refresh_token is None:
            try:
                with open(self.refresh_token_path, encoding='UTF-8') as f:
                    self._refresh_token = f.read().strip()
            except FileNotFoundError:
                self._refresh_token = ''

        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, token):
        with open(self.refresh_token_path, encoding='UTF-8') as f:
            f.write(token)

        self._refresh_token = token
