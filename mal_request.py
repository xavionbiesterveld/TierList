import json
from pathlib import Path
import requests
import hashlib
from dotenv import load_dotenv
import os

load_dotenv('MAL_KEY.env')
MAL_CLIENT_ID  = os.getenv('MAL_CLIENT_ID')
MAL_ACCESS_TOKEN = os.getenv('MAL_ACCESS_TOKEN')
MAL_REFRESH_TOKEN = os.getenv('MAL_REFRESH_TOKEN')

def is_valid_token():
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers={
        'Authorization': f'Bearer {MAL_ACCESS_TOKEN}'
    })

    if response.status_code == 401:
        return False
    if response.status_code >= 500:
        return "Server error"
    else:
        return True

def refresh_tokens():
    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': MAL_CLIENT_ID,
        'grant_type': 'refresh_token',
        'refresh_token': MAL_REFRESH_TOKEN
    }
    response = requests.post(url, data)
    response.raise_for_status()

    token = response.json()
    response.close()

    access_token = token['access_token']
    refresh_token = token['refresh_token']

    env_vars = {}
    dotenv_file = Path('MAL_KEY.env')

    if dotenv_file.exists():
        with open(dotenv_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1) if "=" in line else (line, "")
                    env_vars[key.strip()] = value.strip()

    env_vars["MAL_ACCESS_TOKEN"] = access_token
    env_vars["MAL_REFRESH_TOKEN"] = refresh_token

    try:
        with open(dotenv_file, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
    except IOError as e:
        print(f"Error writing to {'MAL_KEY.env'}: {e}")

    if is_valid_token():
        return True
    else:
        return False


def get_mal_list(user_name: str):
    url = f'https://api.myanimelist.net/v2/users/{user_name}/animelist'
    headers = {'Authorization': f'Bearer {MAL_ACCESS_TOKEN}'}
    r = requests.get(url, headers=headers)

    if r.ok:
        print('ok')
    else:
        print(f'Error: {r.status_code}')

get_mal_list('xavion03')