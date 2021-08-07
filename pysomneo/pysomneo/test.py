import requests
import json
from requests_oauthlib import OAuth2Session

client_id = "api-rob-b130d8f5123bf24b"
client_secret = "c1d91661eef0bc4fa2ac67fd"

authorization_base_url = "https://api.thermosmart.com/oauth2/authorize"
token_url = "https://api.thermosmart.com/oauth2/token"
redirect_uri = "https://google.com/"

session = OAuth2Session(client_id,redirect_uri = redirect_uri)


authorization_url, state = session.authorization_url(authorization_base_url)
print(authorization_url)

redirect_response = input()
redirect_response = redirect_response[0:-1]

token = session.fetch_token(token_url, client_secret=client_secret,authorization_response=redirect_response)

print(token)


"""
payload = {'username': 'demo@thermosmart.com','password': 'demo'}
s = requests.Session()
s.post('https://api.thermosmart.com/login',data=payload)

url = 'https://api.thermosmart.com/oauth2/authorize?redirect_uri=https://home.ruudvdhorst.nl&client_id=api-rob-b130d8f5123bf24b&response_type=code'
response = s.get(url)
trans_id = response.text.split("value=\"")[1].split("\">")[0]
print(trans_id)

payload = {'transaction_id': trans_id}
response = s.post('https://api.thermosmart.com/oauth2/authorize/decision', data=payload)

print(response.text)
print(response.json)

"""
