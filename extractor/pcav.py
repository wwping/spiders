
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

baseUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Referer': 'http://www.stats.gov.cn',
    'cookie': '_trs_uv=k9y68nak_6_58pi; __utma=207252561.911584150.1589012719.1589012719.1589012719.1; __utmz=207252561.1589012719.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); AD_RS_COOKIE=20080918; _trs_ua_s_1=ka0yem3t_6_gw60',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # ':authority': 'm.mzitu.com'
}

length = 0

savePath = ''


class MyThread(Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return []


def getPath(path):
    html = path.split('/')[-1]
    arr = re.findall(r'[0-9]{2}', html.split('.')[0])
    arr.pop()
    arr.append(html)
    res = []
    for i in arr:
        if i != '00':
            res.append(i)
    return f'{baseUrl}{"/".join(res)}'


def saveData(data, name='all'):
    with open(f'{savePath}{sep}address-{name}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))
        f.close


def dataExists(name):
    return os.path.exists(f'{savePath}{sep}address-{name}.json')


def readData(path):
    result = []
    global length

    print(path)

    try:
        rep = requests.get(path, headers=headers, timeout=2)
    except Exception:
        print('timeout')
        time.sleep(2)
        return readData(path)

    if rep.status_code != 200:
        print(rep.status_code)
        time.sleep(2)
        return readData(path)
    rep.encoding = 'gbk'
    html = BeautifulSoup(rep.text, 'lxml')
    ptable = html.find_all(name='table', attrs={'class': 'provincetable'})
    if ptable and len(ptable) > 0:
        tasks = []
        for tr in ptable[0].find_all(name='tr', attrs={'class': 'provincetr'}):

            for a in tr.find_all(name='a'):
                href = getPath(a.attrs["href"])
                code = a.attrs["href"][0:2]
                saveName = f'{code}-{a.text}'
                if dataExists(saveName):
                    print(f'{saveName} 已存在!')
                    continue
                j = {
                    'name': a.text,
                    'code': a.attrs["href"][0:2],
                    'child': readData(href)
                }
                result.append(j)
                saveData(j, name=saveName)

        length += len(tasks)
        print(length)

        return result

    ctable = html.find_all(name='table', attrs={'class': 'citytable'})
    if ctable and len(ctable) > 0:
        for tr in ctable[0].find_all(name='tr', attrs={'class': 'citytr'}):
            tds = tr.find_all(name='td')

            length += len(tds) / 2

            name = (tds[1].a or tds[1]).text
            code = (tds[0].a or tds[0]).text
            href = ''
            if tds[0].a:
                href = tds[0].a.attrs["href"]
            _json = {
                'name': name,
                'code': code[0:4],
                'child': []
            }
            if(href):
                _json['child'] = readData(f'{getPath(href)}')
            result.append(_json)
        print(length)
        return result

    atable = html.find_all(name='table', attrs={'class': 'countytable'})
    if atable and len(atable) > 0:
        for tr in atable[0].find_all(name='tr', attrs={'class': 'countytr'}):
            tds = tr.find_all(name='td')

            length += len(tds)/2

            name = (tds[1].a or tds[1]).text
            code = (tds[0].a or tds[0]).text
            href = ''
            if tds[0].a:
                href = tds[0].a.attrs["href"]
            _json = {
                'name': name,
                'code': code[0:6],
                'child': []
            }
            if(href):
                _json['child'] = readData(f'{getPath(href)}')
            result.append(_json)
        print(length)
        return result

    ttable = html.find_all(name='table', attrs={'class': 'towntable'})
    if ttable and len(ttable) > 0:
        for tr in ttable[0].find_all(name='tr', attrs={'class': 'towntr'}):
            tds = tr.find_all(name='td')

            length += len(tds)/2

            name = (tds[1].a or tds[1]).text
            code = (tds[0].a or tds[0]).text
            href = ''
            if tds[0].a:
                href = tds[0].a.attrs["href"]
            _json = {
                'name': name,
                'code': code[0:9],
                'child': []
            }
            if(href):
                _json['child'] = readData(f'{getPath(href)}')
            result.append(_json)
        print(length)
        return result

    vtable = html.find_all(name='table', attrs={'class': 'villagetable'})
    if vtable and len(vtable) > 0:
        for tr in vtable[0].find_all(name='tr', attrs={'class': 'villagetr'}):
            tds = tr.find_all(name='td')

            length += len(tds)/3

            name = (tds[2].a or tds[2]).text
            code = (tds[0].a or tds[0]).text
            subcode = (tds[1].a or tds[1]).text
            href = ''
            if tds[0].a:
                href = tds[0].a.attrs["href"]
            _json = {
                'name': name,
                'code': code,
                'subcode': subcode,
                'child': []
            }
            if(href):
                _json['child'] = readData(f'{getPath(href)}')
            result.append(_json)
        print(length)
        return result

    print('没找到，重来~~~~~~~')

    return readData(path)


def get(url: str, savepath: str = 'download', func=None) -> dict:

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    global savePath
    savePath = savepath

    global length
    length = 0
    purl = baseUrl
    res = readData(purl)

    saveData(res)

    print('完成~~~~~~~~~~~')

    return {}


if __name__ == "__main__":

    print(get(input("url: ")))
