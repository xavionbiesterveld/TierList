import json
from pathlib import Path
import requests
import hashlib
from dotenv import load_dotenv
import os
from time import sleep
from logger import get_logger

class MALClient:
    def __init__(self, user_name='x4061691', env_path='MAL_KEY.env'):
        load_dotenv(env_path)
        self.env_path = env_path
        self.MAL_CLIENT_ID = os.getenv('MAL_CLIENT_ID')
        self.MAL_ACCESS_TOKEN = os.getenv('MAL_ACCESS_TOKEN')
        self.MAL_REFRESH_TOKEN = os.getenv('MAL_REFRESH_TOKEN')
        self.responses_dir = 'Responses'
        self.images_dir = 'Images'
        self.user_name = user_name
        self.logger = get_logger(__name__)
        os.makedirs(self.responses_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def is_valid_token(self):
        url = 'https://api.myanimelist.net/v2/users/@me'
        response = requests.get(url, headers={
            'Authorization': f'Bearer {self.MAL_ACCESS_TOKEN}'
        })

        if response.ok:
            self.logger.info("Valid access token")
            return True
        elif response.status_code == 401:
            self.logger.warning("Error: Invalid access token")
            self.logger.warning("Attempting to refresh tokens")
            try:
                self.refresh_tokens()
                return True
            except requests.HTTPError as e:
                self.logger.error("Error refreshing token: {e}")
                return False
        else:
            self.logger.error(f"Error validating token: {response.status_code}")
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
            self.logger.error(f"Error writing tokens to {self.env_path}: {e}")
            return

        self.MAL_ACCESS_TOKEN = access_token
        self.MAL_REFRESH_TOKEN = refresh_token

        self.logger.info("Tokens refreshed successfully")

    @staticmethod
    def hash_list(mal_list):
        return hashlib.sha256(json.dumps(mal_list['data'], sort_keys=True).encode()).hexdigest()

    def get_mal_list(self):
        url = f'https://api.myanimelist.net/v2/users/{self.user_name}/animelist'
        headers = {'Authorization': f'Bearer {self.MAL_ACCESS_TOKEN}'}
        params = {'limit': 1000}
        r = requests.get(url, headers=headers, params=params)
        mal_list = r.json()

        if r.ok:
            self.logger.info('List successfully found')
            mal_list_path = f'{self.responses_dir}/mal_list.json'
            hash_path = f'{self.responses_dir}/hash.txt'
            if not os.path.exists(mal_list_path):
                self.logger.info('No list found, creating new')
                try:
                    with open(hash_path, 'w') as f:
                        f.write(self.hash_list(mal_list))
                except IOError as e:
                    self.logger.error(f"Error writing hash to {hash_path}: {e}")
                    return

                try:
                    with open(mal_list_path, 'w') as f:
                        json.dump(mal_list, f, indent=2)
                except IOError as e:
                    self.logger.error(f"Error writing list to {mal_list_path}: {e}")
                    return

                self.logger.info('New list saved')

            else:
                self.logger.info('Checking for updates')

                new_hash = self.hash_list(mal_list)

                try:
                    with open(hash_path, 'r') as f:
                        old_hash = f.read()
                except IOError as e:
                        self.logger.error(f"Error reading hash from {hash_path}: {e}")
                        return

                if new_hash != old_hash:
                    self.logger.info('Update found, saving new list')
                    try:
                        with open(mal_list_path, 'w') as f:
                            json.dump(mal_list, f, indent=2)
                            self.logger.info('New list saved')
                    except IOError as e:
                        self.logger.error(f"Error writing list to {mal_list_path}: {e}")
                        return

                    try:
                        with open(hash_path, 'w') as f:
                            f.write(new_hash)
                    except IOError as e:
                        self.logger.error(f"Error writing hash to {hash_path}: {e}")
                        return
                else:
                    self.logger.info('No update found')
        else:
            try:
                r.raise_for_status()
            except requests.HTTPError as e:
                self.logger.error(f"Error fetching list: {e}")
                return

    def download_image(self, image_url, anime_id):
        r = requests.get(image_url)
        if r.ok:
            self.logger.debug(f'Image downloaded successfully: {anime_id}')
            with open(f'{self.images_dir}/{anime_id}.jpg', 'wb') as f:
                f.write(r.content)
            return False
        else:
            self.logger.warning(f'Error downloading image: {anime_id}->{r.status_code}')
            return True

    def download_images(self):
        mal_list_path = f'{self.responses_dir}/mal_list.json'
        try:
            with open(mal_list_path, 'r') as f:
                mal_list = json.load(f)
        except FileNotFoundError as e:
            self.logger.error(f"Error opening list file: {e}")
            return
        except IOError as e:
            self.logger.error(f"Error reading list file: {e}")
            return

        for anime in mal_list['data']:
            anime_id = anime["node"]["id"]
            img_path = f'{self.images_dir}/{anime_id}.jpg'
            if not os.path.exists(img_path):
                self.logger.info(f'Downloading image: {anime_id}')
                image_url = anime['node']['main_picture']['large']
                download_error = self.download_image(image_url, anime_id)
                if download_error:
                    break
                sleep(0.30)

    def anime_info_query(self, anime_id):
        url = f'https://api.myanimelist.net/v2/anime/{anime_id}'
        headers = {'Authorization': f'Bearer {self.MAL_ACCESS_TOKEN}'}
        params = {'fields': 'title,mean,rank,popularity,genres,start_season,opening_themes'}
        r = requests.get(url, headers=headers, params=params)
        if r.ok:
            self.logger.debug(f'Anime info found: {anime_id}')
            return r.json()
        else:
            self.logger.error(f'Error: {r.status_code}')
            return None

    def get_anime_info(self):
        mal_list_path = f'{self.responses_dir}/mal_list.json'
        info_json_path = f'{self.responses_dir}/info.json'
        with open(mal_list_path, 'r') as f:
            mal_list = json.load(f)

        # Load or initialize info_dict
        if os.path.exists(info_json_path):
            self.logger.info('Info file found, updating')
            with open(info_json_path, 'r', encoding='utf-8') as f:
                try:
                    info_dict = json.load(f)
                except json.JSONDecodeError:
                    info_dict = {}
        else:
            self.logger.info('No info file found, creating new')
            info_dict = {}

        updated = False
        for anime in mal_list['data']:
            anime_id = str(anime["node"]["id"])
            if anime_id not in info_dict:
                self.logger.info(f'Adding {anime_id} to info dict')
                anime_info = self.anime_info_query(anime["node"]["id"])
                if anime_info:
                    info_dict[anime_id] = anime_info
                    updated = True
                sleep(0.30)

        if updated or not os.path.exists(info_json_path):
            with open(info_json_path, 'w', encoding='utf-8') as f:
                json.dump(info_dict, f, ensure_ascii=False, indent=2)

    def cache_info(self):
        info_json_path = f'{self.responses_dir}/info.json'
        try:
            with open(info_json_path, 'r', encoding='utf-8') as f:
                info = json.load(f)

            self._info_dict = info
            self.logger.info("Info dict cached successfully")

        except FileNotFoundError:
            self.logger.error("Info file not found")

    def get_info(self, id):
        try:
            info = self._info_dict[str(id)]
            return info
        except KeyError:
           self.logger.error(f'Anime info not found for {id}')


if __name__ == '__main__':
    client = MALClient()
    if client.is_valid_token():
        client.get_mal_list()
        client.download_images()
        client.get_anime_info()
        client.cache_info()
        print(client.get_info(5081))
    else:
        print("Invalid access token")