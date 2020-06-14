'''
@Author: your name
@Date: 2020-06-09 12:51:24
@LastEditTime: 2020-06-14 23:13:18
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: \spiders\extractor\douyin.py
'''
import re

import requests


import re
from extractor import douyin_user
from extractor import douyin_video

headers = {
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
}


def get(url: str, savepath: str = 'download', func=None) -> dict:

    rep = requests.get(url, headers=headers,
                       allow_redirects=False, verify=False)
    location = rep.headers['Location']

    if '/share/user/' in location:
        return douyin_user.get(url, func=func)
    else:
        data = douyin_video.get(url, func=func)
        return data

    return {}


if __name__ == "__main__":
    print(get(input("url: ")))
