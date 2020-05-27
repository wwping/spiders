
import re
import requests
import os
import time
import random
import threading
from threading import Thread
from bs4 import BeautifulSoup
import json
import click
sep = os.sep

baseUrl = 'http://www.zzzttt.vip/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Referer': 'http://www.zzzttt.vip/',
    'cookie': 'UM_distinctid=171f980002a6df-0d24bd6dea1689-7373667-1fa400-171f980002bad6; CNZZDATA1278872624=2101708887-1589026699-%7C1589075301',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # ':authority': 'm.mzitu.com'
}

savePath = ''


def filterName(name):
    regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$\n|\.|\s)')
    space = re.compile(r'\s{2,}')
    name = space.sub(" ", regexp.sub("", name))
    return name


def readData(url):
    global savePath
    rep = requests.get(url, headers=headers, timeout=5)

    html = BeautifulSoup(rep.text, 'lxml')

    li = html.find_all(name='li', attrs={'class': 'next'})
    nextPage = ''
    if li and len(li) > 0:
        nextPage = li[0].a.attrs['href']

    for art in html.find_all(name='article', attrs={'itemtype': 'http://schema.org/BlogPosting'}):

        href = art.a.attrs['href']
        if href:
            print(href)
            rep = requests.get(href, headers=headers, timeout=5)
            html = BeautifulSoup(rep.text, 'lxml')
            title = html.find_all(
                name='h1', attrs={'class': 'post-title'})[0].text
            index = 0

            urls = []
            for video in html.find_all(name='video'):
                urls.append(video.attrs['src'])

            for a in html.find_all(name='a'):
                try:
                    _href = a.attrs['href']
                    if 'https://nim-nosdn.netease.im' in _href:
                        urls.append(_href)
                except BaseException:
                    pass

            for dpath in urls:
                filename = savePath+sep + \
                    filterName(title)+'_'+str(index)+'.mp4'

                if os.path.exists(filename):
                    print(f'{filename} 已存在')
                    index += 1
                    continue

                print(f'{filename} 开始下载')
                try:
                    with requests.get(dpath, headers=headers, stream=True, timeout=30) as rep:
                        file_size = int(rep.headers['Content-Length'])
                        if rep.status_code != 200:
                            print(f'{title} 下载失败')
                            continue
                        label = '{:.2f}MB'.format(file_size / (1024 * 1024))
                        with click.progressbar(length=file_size, label=label) as progressbar:
                            with open(filename, "wb") as f:
                                for chunk in rep.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                                        progressbar.update(1024)
                except BaseException:
                    pass
                index += 1
    if nextPage:
        readData(nextPage)


def get(url: str, savepath: str = 'download', func=None) -> dict:

    global savePath
    savePath = savepath
    savePath = savepath+sep + 'zzzttt'
    if not os.path.exists(savePath):
        os.makedirs(savePath)

    readData('http://www.zzzttt.vip/')

    print('完成~~~~~~~~~~~')

    return {}


if __name__ == "__main__":

    print(get(input("url: ")))
