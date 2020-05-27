
import re
from urllib.parse import unquote

import requests

from .encrypt import Cracker


class Wangyiyun():
    def __init__(self):
        self.headers = {
            'Referer': 'https://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.32 Safari/537.36'
        }
        self.headers2 = {
            'Referer': 'https://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.16'
        }
        self.music_url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
        self.mv_url = "https://music.163.com/weapi/song/enhance/play/mv/url?csrf_token="

    def get(self, url):
        """
        返回资源链接
        """

        if "video" in url:
            return {
                'url': self.get_video(url),
                'name': ''
            }
        id = self.get_id(url)
        if "mv" in url:
            params = {"id": id, "r": "1080", "csrf_token": ""}
            data = self.__postRequests(self.mv_url, params)
            if data:
                return {
                    'url': data["data"]["url"],
                    'name': ''
                }
        elif "song" in url:
            params = {'ids': [int(id)], 'br': 320000, 'csrf_token': ''}
            data = self.__postRequests(self.music_url, params)
            rep = requests.get(url,
                               headers=self.headers2)
            # print(rep.text)
            name = re.findall(r'"title": "(.*?)",', rep.text)
            if name:
                name = name[0]
            if data:
                return {
                    'url': data["data"][0]["url"],
                    'name': name or None
                }
        return None

    def get_video(self, url):
        id = self.get_id(url)
        url = f"http://music.163.com/video/{id}/"
        rep = requests.get(url, headers=self.headers, timeout=6)
        if rep.status_code == 200:
            encoded_url = re.findall(
                r'<meta property="og:video" content="(.*?)" />', rep.text)[0]
            return unquote(encoded_url)
        return None

    # 匹配id
    def get_id(self, raw_url) -> str:
        pattern1 = re.compile(r'\?id=(\w+)')
        pattern2 = re.compile(r'song/(\w+)/')
        pattern3 = re.compile(r'mv/(\w+)/')
        pattern4 = re.compile(r'video/(\w+)/')
        if "?id" in raw_url:
            id = re.findall(pattern1, raw_url)
        elif "song" in raw_url:
            id = re.findall(pattern2, raw_url)
        elif "mv" in raw_url:
            id = re.findall(pattern3, raw_url)
        elif "video" in raw_url:
            id = re.findall(pattern4, raw_url)
        if id:
            return id[0]
        return None

    def __postRequests(self, url, params, timeout=6):
        post_data = Cracker.get(params)
        rep = requests.post(url,
                            data=post_data,
                            timeout=timeout,
                            headers=self.headers)
        if rep.json()['code'] == 200:
            return rep.json()
        return None
