# Fetch OAuth2 token via client credentials
import os, requests
from time import time

_token_cache = {"expiry": 0, "token": None}

def get_token():
    creds = {
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "grant_type": "client_credentials",
        "scope": os.environ.get("SCOPES", "")
    }
    endpoint = os.environ["TOKEN_ENDPOINT"]
    if _token_cache["token"] and time() < _token_cache["expiry"] - 30:
        return _token_cache["token"]
    resp = requests.post(endpoint, data=creds, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    _token_cache.update({
        "token": token,
        "expiry": time() + data.get("expires_in", 300)
    })
    return token
