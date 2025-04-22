import json
from pathlib import Path
import requests
import hashlib
from dotenv import load_dotenv
import os
from time import sleep

class MALClient:
    def __init__(self, env_path='MAL_KEY.env'):
        load_dotenv(env_path)
        self.env_path = env_path
        self.MAL_CLIENT_ID = os.getenv('MAL_CLIENT_ID')
        self.MAL_ACCESS_TOKEN = os.getenv('MAL_ACCESS_TOKEN')
        self.MAL_REFRESH_TOKEN = os.getenv('MAL_REFRESH_TOKEN')
        self.responses_dir = 'Responses'
        self.images_dir = 'Images'
        os.makedirs(self.responses_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def is_valid_token(self):
        url = 'https://api.myanimelist.net/v2/users/@me'
        response = requests.get(url, headers={
            'Authorization': f'Bearer {self.MAL_ACCESS_TOKEN}'
        })

        if response.ok:
            print("Valid access token")
            return True
        elif response.status_code == 401:
            print("Error: Invalid access token")
            print("Attempting to refresh tokens")
            try:
                self.refresh_tokens()
                return True
            except:
                print("Error refreshing token")
                return False
        else:
            print(f"Error: {response.status_code}")
            return False

    def refresh_tokens(self):
        url = 'https://myanimelist.net/v1/oauth2/token'
        data = {
            'client_id': self.MAL_CLIENT_ID,
            'grant_type': 'refresh_token',
            'refresh_token': self.MAL_REFRESH_TOKEN
        }
        response = requests.post(url, data)
        response.raise_for_status()
        token = response.json()
        response.close()

        access_token = token['access_token']
        refresh_token = token['refresh_token']
        env_vars = {}
        dotenv_file = Path(self.env_path)

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
            print(f"Error writing to {self.env_path}: {e}")

        self.MAL_ACCESS_TOKEN = access_token
        self.MAL_REFRESH_TOKEN = refresh_token

        print("Tokens refreshed successfully")

    @staticmethod
    def hash_list(mal_list):
        return hashlib.sha256(json.dumps(mal_list['data'], sort_keys=True).encode()).hexdigest()

    def get_mal_list(self, user_name: str):
        url = f'https://api.myanimelist.net/v2/users/{user_name}/animelist'
        headers = {'Authorization': f'Bearer {self.MAL_ACCESS_TOKEN}'}
        params = {'limit': 1000}
        r = requests.get(url, headers=headers, params=params)
        mal_list = r.json()

        if r.ok:
            print('List successfully found')
            mal_list_path = f'{self.responses_dir}/mal_list.json'
            hash_path = f'{self.responses_dir}/hash.txt'
            if not os.path.exists(mal_list_path):
                print('No list found, creating new')
                with open(hash_path, 'w') as f:
                    f.write(self.hash_list(mal_list))
                with open(mal_list_path, 'w') as f:
                    json.dump(mal_list, f, indent=2)
                print('New list saved')
            else:
                print('List found, checking for updates')
                new_hash = self.hash_list(mal_list)
                with open(hash_path, 'r') as f:
                    old_hash = f.read()
                if new_hash != old_hash:
                    print('Update found, saving new list')
                    with open(mal_list_path, 'w') as f:
                        json.dump(mal_list, f, indent=2)
                        print('New list saved')
                    with open(hash_path, 'w') as f:
                        f.write(new_hash)
                else:
                    print('No update found')
        else:
            print(f'Error: {r.status_code}')

    def download_image(self, image_url, anime_id):
        r = requests.get(image_url)
        if r.ok:
            print(f'Image downloaded successfully: {anime_id}')
            with open(f'{self.images_dir}/{anime_id}.jpg', 'wb') as f:
                f.write(r.content)
            return False
        else:
            print(f'Error downloading image: {anime_id}->{r.status_code}')
            return True

    def download_images(self, num=20):
        mal_list_path = f'{self.responses_dir}/mal_list.json'
        with open(mal_list_path, 'r') as f:
            mal_list = json.load(f)
        for anime in range(20):
            anime_id = mal_list['data'][anime]['node']['id']
            img_path = f'{self.images_dir}/{anime_id}.jpg'
            if not os.path.exists(img_path):
                image_url = mal_list['data'][anime]['node']['main_picture']['large']
                download_error = self.download_image(image_url, anime_id)
                if download_error:
                    break
                sleep(0.50)
            else:
                print(f'Image already exists: {anime_id}')
