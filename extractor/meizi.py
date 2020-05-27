

import re
import requests
import os
import time
import random
from bs4 import BeautifulSoup
import json
sep = os.sep

ips = ['118.24.128.46:1080', '118.113.247.171:9999', '222.240.184.126:8086', '31.14.131.70:8080', '121.237.149.100:3000', '119.27.177.238:8080', '182.32.251.226:9999', '39.137.69.9:8080', '1.202.193.26:59212', '115.239.32.115:9000', '60.211.218.78:53281', '180.125.120.240:24906', '221.122.91.74:9401', '123.168.138.220:9999', '117.69.150.69:4216', '101.4.136.34:81', '47.104.15.198:80', '222.218.123.99:9999', '121.40.108.76:80', '122.233.234.32:8118', '124.234.55.16:8118', '211.144.213.145:80', '117.69.170.186:4216', '49.70.94.144:54030', '183.166.163.103:4216', '171.35.172.213:9999', '171.35.171.14:9999', '163.204.240.136:9999', '125.123.16.41:9000', '118.89.150.177:1080', '113.195.152.125:9999', '221.122.91.59:80', '223.100.166.3:36945', '171.35.172.89:9999', '139.199.153.25:1080', '60.216.101.46:32868', '124.112.105.141:4216', '113.124.92.211:9999', '113.120.146.170:9999', '118.113.247.142:9999', '58.220.95.79:10000', '120.83.109.19:9999', '123.207.217.104:1080', '120.83.111.251:9999', '182.46.216.185:9999', '49.235.253.240:8888', '117.69.178.46:4216', '183.223.241.242:80', '119.57.108.213:53281', '118.24.88.240:1080',
       '115.221.208.220:9999', '110.243.0.101:9999', '118.24.127.144:1080', '123.132.232.254:61017', '123.207.57.92:1080', '113.121.189.63:35559', '110.243.6.219:9999', '120.83.107.93:9999', '183.166.250.187:4216', '123.153.94.130:22204', '118.212.104.7:9999', '120.83.103.123:9999', '58.251.232.154:9797', '218.27.136.169:8085', '118.89.51.66:5000', '49.85.99.29:10098', '58.253.152.246:9999', '163.204.246.87:9999', '221.13.156.158:55443', '218.59.193.14:43995', '118.24.90.160:1080', '171.35.167.218:9999', '58.246.3.178:53281', '183.230.179.164:8060', '221.122.91.65:80', '104.250.34.179:80', '114.249.112.89:9000', '120.83.99.48:9999', '58.220.95.90:9401', '115.29.42.152:80', '120.27.199.129:8089', '106.110.97.208:4216', '182.46.251.126:9999', '115.221.241.88:9999', '61.240.222.27:3128', '103.44.145.182:8080', '182.34.33.30:9999', '163.125.158.242:8888', '111.222.141.127:8118', '58.251.232.155:9797', '163.204.244.200:9999', '163.204.247.118:9999', '52.81.33.108:80', '121.226.17.163:39895', '125.111.193.176:49733', '183.166.252.62:4216', '101.200.36.219:80', '115.221.243.116:9999', '113.124.92.48:9999', '222.184.7.206:36770']


def randomip():
    ip = random.sample(ips, 1)[0]
    return {
        'http': 'http://'+ip,
        'https': 'http://'+ip
    }


def filterName(name):
    regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$)')
    space = re.compile(r'\s{2,}')
    return space.sub(" ", regexp.sub("", name))
# 获取cid, bv_id, ep_id, 当前集数


def checkDir(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def get(url: str, savepath: str = 'download', func=None) -> dict:

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Referer': 'https://www.mzitu.com',
        'Referrer-Policy': 'origin',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': 'UM_distinctid=171e374086d8-0321a75e123df2-5437971-3d10d-171e374086eb22; Hm_lvt_cb7f29be3c304cd3bb0c65a4faa96c30=1588656567,1588665502; Hm_lpvt_cb7f29be3c304cd3bb0c65a4faa96c30=1588665504',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # ':authority': 'm.mzitu.com'
    }

    url = 'https://m.mzitu.com/all/'

    proxies = {}  # randomip()

    rep = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(rep.text, 'lxml')
    lists = soup.find_all(name='div', attrs={'id': 'post-archives'})[0]

    savepath = 'F:'+sep+'资源下载'+sep+'mzitu'

    rootPath = savepath
    _savePath = savepath
    __savePath = savepath

    res = []
    images = []

    index = 0
    total = 0

    for div in lists.find_all(name='div'):
        h3 = div.find_all('h3')
        if h3:
            res.append({
                'type': 'group',
                'text': filterName(h3[0].text)
            })
        else:

            a = div.find_all('a')[0]
            href = a.attrs['href']
            text = a.text
            res.append({
                'type': 'item',
                'href': href,
                'text': filterName(text)
            })
    '''
    with open(rootPath+sep+'1.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(res))
        f.close
    # print(_savePath)
    # print(res)
    # return{}
    return{}
    '''
    for item in res:
        if item['type'] == 'group':
            _savePath = rootPath + sep + item['text']
            checkDir(_savePath)
            continue
        else:
            try:
                __savePath = _savePath + sep + item['text']
                checkDir(__savePath)
                headers['Referer'] = item['href']
                rep = requests.get(
                    item['href'], headers=headers, proxies=proxies)

                soup = BeautifulSoup(rep.text, 'lxml')

                text = soup.find_all(name='span', attrs={
                    'class': 'prev-next-page'})[0].text
                pages = int(re.findall(r'1/([0-9]*)页', text)[0])

                for i in range(pages):

                    p = i+1

                    _url = f'{item["href"]}/{p}'
                    headers['Referer'] = _url
                    rep = requests.get(_url, headers=headers, proxies=proxies)
                    soup = BeautifulSoup(rep.text, 'lxml')

                    filename = __savePath + sep + f'{p}.jpg'
                    if os.path.exists(filename):
                        print(f'{filename} 文件已存在', end='\r', flush=True)
                        continue
                    try:
                        image = soup.find_all(name='figure')[
                            0].p.a.img.attrs['src']
                        with requests.get(image, headers=headers, stream=True, proxies=proxies) as rep:
                            with open(filename, "wb") as f:
                                for chunk in rep.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)

                        total += 1
                        print(f'{total} 张', end='\r', flush=True)
                        images.append({
                            'savePath': _savePath,
                            'saveName': f'{p}.jpg',
                            'src': image
                        })
                    except BaseException:
                        pass
                    time.sleep(0.5)
                time.sleep(1)
            except BaseException:
                pass
    print(len(images))
    '''
        # post-archives
            .archive-header
                h3
            .archive-brick
                a href
    '''
    # print(rep.text)

    return {}


if __name__ == "__main__":
    print(get(input("url: ")))
