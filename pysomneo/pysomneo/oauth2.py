import base64
import requests
import os
import json
import sys
from urllib.parse import urlencode

class ThermosmartOauthError(Exception):
    pass

class ThermosmartOAuth(object):
    '''
    Implements Authorization Code Flow for Thermosmart's OAuth implementation.
    '''

    OAUTH_AUTHORIZE_URL = 'https://api.thermosmart.com/oauth2/authorize'
    OAUTH_TOKEN_URL = 'https://api.thermosmart.com/oauth2/token'

    def __init__(self, client_id, client_secret, redirect_uri, cache_path=None):
        '''
            Creates a ThermosmartOAuth object
            Parameters:
                 - client_id - the client id of your app
                 - client_secret - the client secret of your app
                 - redirect_uri - the redirect URI of your app
                 - cache_path - path to location to save tokens
        '''

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.cache_path = cache_path

    def get_cached_token(self):
        ''' Gets a cached auth token
        '''
        token_info = None
        if self.cache_path:
            try:
                f = open(self.cache_path)
                token_info_string = f.read()
                f.close()
                token_info = json.loads(token_info_string)

            except IOError:
                pass
        return token_info

    def _save_token_info(self, token_info):
        if self.cache_path:
            try:
                f = open(self.cache_path, 'w')
                f.write(json.dumps(token_info))
                f.close()
            except IOError:
                self._warn("couldn't write token cache to " + self.cache_path)
                pass

    def get_authorize_url(self):
        """ Gets the URL to use to authorize this app
        """
        payload = {"client_id": self.client_id,
                   "response_type": "code",
                   "redirect_uri": self.redirect_uri,
                   "scope": "ot"}

        urlparams = urlencode(payload)

        return "%s?%s" % (self.OAUTH_AUTHORIZE_URL, urlparams)


    def parse_response_code(self, url):
        """ Parse the response code in the given response url
            Parameters:
                - url - the response url
        """
        try:
            return url.json.split("?code=")[1].split("&")[0]
        except IndexError:
            return None

    def _make_authorization_headers(self):
        auth_header = base64.b64encode((self.client_id + ':' + self.client_secret).encode('ascii'))
        return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

    def get_access_token(self, code):
        """ Gets the access token for the app given the code
            Parameters:
                - code
        """
        payload = {'redirect_uri': self.redirect_uri,
                   'code': code,
                   'grant_type': 'authorization_code',
                   'scope': 'ot'}

        headers = self._make_authorization_headers()

        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers)
        if response.status_code != 200:
            raise ThermosmartOauthError(response.reason)
        token_info = response.json()
        self._save_token_info(token_info)
        return token_info

    def _warn(self, msg):
        print('warning:' + msg, file=sys.stderr)