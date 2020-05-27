
import re
import requests
import os
import time
import random
import threading
from bs4 import BeautifulSoup
import json
import click
import subprocess
sep = os.sep


sem = threading.Semaphore(30)


def filterName(name):
    regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$\n|\.|\s)')
    space = re.compile(r'\s{2,}')
    name = space.sub(" ", regexp.sub("", name))
    return name
# 获取cid, bv_id, ep_id, 当前集数


baseUrl = 'https://www.qke866.com'


def checkDir(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def downloadFile(url, filename, headers):
    with sem:
        try:
            with requests.get(url, headers=headers, stream=True, timeout=5) as rep:
                file_size = int(rep.headers['Content-Length'])
                if rep.status_code != 200:
                    print(f'{filename} 下载失败')
                    return False
                label = '{:.2f}MB'.format(
                    file_size / (1024 * 1024))
                with click.progressbar(length=file_size, label=label) as progressbar:
                    with open(filename, "wb") as f:
                        for chunk in rep.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                progressbar.update(1024)
        except Exception:
            downloadFile(url, filename, headers)


def concatContent(filename):
    content = "file '"+filename+"'\n"
    return content


def writeConcatFile(content):
    with open('task.txt', 'w', encoding='utf-8') as f:
        f.write(content)
        f.close


def videoMerge(output, title=''):
    print(f"\n【{title}】 分块视频合并中....................")
    sentence = 'ffmpeg -loglevel error -f concat -safe 0 -i "{}" -c copy "{}" -y'.format(
        'task.txt', output)
    child = subprocess.Popen(sentence, shell=True)
    child.wait()
    os.remove('task.txt')
    print(f"\n【{title}】 分块视频合并完成....................")


def xiazai(savepath, name, page=1, func=None):

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Referer': baseUrl,
        'Referrer-Policy': 'origin',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '__cfduid=dea732ee4830bda9d83d805245c1c20ce1588671139; UM_distinctid=171e42dd960b9d-0bf83b15df3a71-7373667-1fa400-171e42dd961ae8; CNZZDATA1278201352=462699466-1588667605-%7C1588667605; Hm_lvt_f81ddd647520c9511702993cce9f0c8f=1588671142; Hm_lvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671142; _ga=GA1.2.104118330.1588671142; _gid=GA1.2.526591924.1588671142; playss=4; Hm_lpvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671192; Hm_lpvt_f81ddd647520c9511702993cce9f0c8f=1588671192',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # ':authority': 'm.mzitu.com'
    }

    url = baseUrl+'/xiazai/list-国产自拍.html'

    rep = requests.get(url, headers=headers)
    soup = BeautifulSoup(rep.text, 'lxml')

    pages = int(re.findall(
        r'1/([0-9]*)', soup.find_all(name='a', attrs={'class': 'visible-xs'})[0].text)[0])

    rootPath = savepath + sep + 'hhr279'+sep+'奇怪视频下载'
    checkDir(rootPath)

    for i in range(page, pages):
        try:
            p = i
            func(name, p)
            print(f'\n{name} 第 {p} 页 开始')

            _url = f'{baseUrl}/xiazai/list-国产自拍-{p}.html'
            rep = requests.get(_url, headers=headers)
            rep.encoding = 'utf8'
            soup = BeautifulSoup(rep.text, 'lxml')

            wrap = soup.find_all(name='div',
                                 attrs={'id': 'tpl-img-content'})[0]
            print(f'\n{name}  第 {p} 页 拉取完成')
            print(f'\n{name}  第 {p} 页 开始下载')
            index = 0
            for li in wrap.find_all(name='li'):

                title = li.a.attrs['title']

                filename = rootPath + sep + \
                    filterName(title) + '.mp4'

                print(f'\n{name}  第 {p} 页 第{index+1}段 {title} 开始读取')

                rep = requests.get(baseUrl +
                                   li.a.attrs['href'], headers=headers)
                rep.encoding = 'utf8'
                soup = BeautifulSoup(rep.text, 'lxml')

                mp4 = soup.find_all(name='input', attrs={'id': 'lin1k0'})[
                    0].attrs['value']

                if os.path.exists(filename):
                    index += 1
                    print(f'{name} 文件已存在')
                    continue
                print(f'\n{name}  第 {p} 页 第{index+1}段 {title} 开始下载')
                print(mp4)
                try:
                    with requests.get(mp4, headers=headers, stream=True, timeout=30) as rep:
                        file_size = int(rep.headers['Content-Length'])
                        if rep.status_code != 200:
                            print(f'{name} 下载失败')
                            return False
                        label = '{:.2f}MB'.format(file_size / (1024 * 1024))
                        with click.progressbar(length=file_size, label=label) as progressbar:
                            with open(filename, "wb") as f:
                                for chunk in rep.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                                        progressbar.update(1024)
                except BaseException:
                    pass
                print(f'\n{name} 第 {p} 页 第{index+1}段 {title} 下载完成')
                time.sleep(1)
                index += 1
        except BaseException:
            pass


def tupian(savepath, name, page=1, func=None):

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Referer': baseUrl,
        'Referrer-Policy': 'origin',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '__cfduid=dea732ee4830bda9d83d805245c1c20ce1588671139; UM_distinctid=171e42dd960b9d-0bf83b15df3a71-7373667-1fa400-171e42dd961ae8; CNZZDATA1278201352=462699466-1588667605-%7C1588667605; Hm_lvt_f81ddd647520c9511702993cce9f0c8f=1588671142; Hm_lvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671142; _ga=GA1.2.104118330.1588671142; _gid=GA1.2.526591924.1588671142; playss=4; Hm_lpvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671192; Hm_lpvt_f81ddd647520c9511702993cce9f0c8f=1588671192',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # ':authority': 'm.mzitu.com'
    }

    url = f'{baseUrl}/tupian/list-%E8%87%AA%E6%8B%8D%E5%81%B7%E6%8B%8D.html'

    rep = requests.get(url, headers=headers)
    soup = BeautifulSoup(rep.text, 'lxml')

    pages = int(re.findall(
        r'1/([0-9]*)', soup.find_all(name='a', attrs={'class': 'visible-xs'})[0].text)[0])

    rootPath = savepath + sep + 'hhr279'+sep+'奇怪图片'
    _savePath = rootPath + sep + 'hhr279'+sep+'奇怪图片'

    for p in range(page, pages):
        func(name, p)
        print(f'{name} 第 {p} 页 开始')

        _savePath = rootPath
        checkDir(_savePath)

        _url = f'{baseUrl}/tupian/list-自拍偷拍-{p}.html'
        rep = requests.get(_url, headers=headers)
        rep.encoding = 'utf8'
        soup = BeautifulSoup(rep.text, 'lxml')

        wrap = soup.find_all(name='ul',
                             attrs={'id': 'grid'})[0]
        print(f'{name} 第 {p} 页 拉取完成')
        print(f'{name} 第 {p} 页 开始下载')
        index = 0
        for li in wrap.find_all(name='li'):

            a = li.find_all(name='a', attrs={'target': '_blank'})[0]
            title = a.attrs['title']
            _path = _savePath + sep + filterName(title)
            checkDir(_path)

            print(f'\n{name} 第 {p} 页 第{index+1}段 {title} 开始下载')

            rep = requests.get(baseUrl +
                               a.attrs['href'], headers=headers)
            rep.encoding = 'utf8'
            soup = BeautifulSoup(rep.text, 'lxml')
            images = soup.find_all(name='img', attrs={'class': 'videopic'})
            _imgindex = 0
            for img in images:
                print(
                    f'\n{name} 第 {p} 页 第{index+1}段 {title} 第{_imgindex+1}张 开始下载')
                imgUrl = img.attrs['data-original']
                print(imgUrl)
                filename = _path + sep + str(_imgindex)+'.jpg'

                if os.path.exists(filename):
                    print(f'{name} 文件已存在')
                    continue
                try:
                    with requests.get(imgUrl, headers=headers, stream=True, timeout=30) as rep:
                        file_size = int(rep.headers['Content-Length'])
                        if rep.status_code != 200:
                            print(f'{name} 下载失败')
                            return False
                        label = '{:.2f}MB'.format(file_size / (1024 * 1024))
                        with click.progressbar(length=file_size, label=label) as progressbar:
                            with open(filename, "wb") as f:
                                for chunk in rep.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                                        progressbar.update(1024)
                except BaseException:
                    pass

                time.sleep(1)
                print(
                    f'{name} 第 {p} 页 第{index+1}段 {title} 第{_imgindex+1}张 下载完成')
                _imgindex += 1

            print(f'\n{name} 第 {p} 页 第{index+1}段 {title} 下载完成')
            index += 1

    return {}


def shipin(savepath, name, page=1, func=None):

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Referer': baseUrl,
        'Referrer-Policy': 'origin',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '__cfduid=dea732ee4830bda9d83d805245c1c20ce1588671139; UM_distinctid=171e42dd960b9d-0bf83b15df3a71-7373667-1fa400-171e42dd961ae8; CNZZDATA1278201352=462699466-1588667605-%7C1588667605; Hm_lvt_f81ddd647520c9511702993cce9f0c8f=1588671142; Hm_lvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671142; _ga=GA1.2.104118330.1588671142; _gid=GA1.2.526591924.1588671142; playss=4; Hm_lpvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671192; Hm_lpvt_f81ddd647520c9511702993cce9f0c8f=1588671192',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # ':authority': 'm.mzitu.com'
    }

    url = baseUrl+'/shipin/list-短视频.html'

    rep = requests.get(url, headers=headers)
    soup = BeautifulSoup(rep.text, 'lxml')

    pages = int(re.findall(
        r'1/([0-9]*)', soup.find_all(name='a', attrs={'class': 'visible-xs'})[0].text)[0])

    rootPath = savepath + sep + 'hhr279'+sep+'奇怪视频-' + \
        time.strftime("%Y-%m-%d", time.localtime())
    checkDir(rootPath)

    for i in range(page, pages):
        try:
            p = i
            func(name, p)
            print(f'\n{name} 第 {p} 页 开始')

            _url = f'{baseUrl}/shipin/list-短视频-{p}.html'
            rep = requests.get(_url, headers=headers)
            rep.encoding = 'utf8'
            soup = BeautifulSoup(rep.text, 'lxml')

            wrap = soup.find_all(name='ul',
                                 attrs={'class': 'content-list'})[0]

            print(f'\n{name} 第 {p} 页 拉取完成')
            print(f'\n{name} 第 {p} 页 开始下载')
            index = 0
            for li in wrap.find_all(name='li'):

                title = li.a.attrs['title']

                filename = rootPath + sep + \
                    filterName(title) + '.mp4'

                print(f'\n{name} 第 {p} 页 第{index+1}段 {title} 开始读取')

                rep = requests.get(baseUrl +
                                   li.a.attrs['href'], headers=headers, timeout=30)
                rep.encoding = 'utf8'
                soup = BeautifulSoup(rep.text, 'lxml')

                mp4 = soup.find_all(name='input', attrs={'id': 'lin1k0'})[
                    0].attrs['value']

                if os.path.exists(filename):
                    index += 1
                    print(f'{name} 文件已存在')
                    continue

                print(f'\n{name} 第 {p} 页 第{index+1}段 {title} 开始下载')
                print(mp4)
                try:
                    with requests.get(mp4, headers=headers, stream=True, timeout=30) as rep:
                        file_size = int(rep.headers['Content-Length'])
                        if rep.status_code != 200:
                            print(f'{name} 下载失败')
                            return False
                        label = '{:.2f}MB'.format(file_size / (1024 * 1024))
                        with click.progressbar(length=file_size, label=label) as progressbar:
                            with open(filename, "wb") as f:
                                for chunk in rep.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                                        progressbar.update(1024)
                except BaseException:
                    pass
                print(f'\n{name} 第 {p} 页 第{index+1}段 {title} 下载完成')
                time.sleep(1)
                index += 1
        except BaseException:
            pass


def guochan(savepath, name, page=1, func=None):

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Referer': baseUrl,
        'Referrer-Policy': 'origin',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '__cfduid=dea732ee4830bda9d83d805245c1c20ce1588671139; UM_distinctid=171e42dd960b9d-0bf83b15df3a71-7373667-1fa400-171e42dd961ae8; CNZZDATA1278201352=462699466-1588667605-%7C1588667605; Hm_lvt_f81ddd647520c9511702993cce9f0c8f=1588671142; Hm_lvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671142; _ga=GA1.2.104118330.1588671142; _gid=GA1.2.526591924.1588671142; playss=4; Hm_lpvt_b579a2b4f34aaa4e32faf06b2a699fb2=1588671192; Hm_lpvt_f81ddd647520c9511702993cce9f0c8f=1588671192',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # ':authority': 'm.mzitu.com'
    }

    url = baseUrl+'/shipin/list-国产精品.html'

    rep = requests.get(url, headers=headers)
    soup = BeautifulSoup(rep.text, 'lxml')

    pages = int(re.findall(
        r'1/([0-9]*)', soup.find_all(name='a', attrs={'class': 'visible-xs'})[0].text)[0])

    rootPath = savepath + sep + 'hhr279'+sep+'奇怪视频国产'
    checkDir(rootPath)

    for p in range(page, pages):
        func(name, p)
        print(f'{name} 第 {p} 页 开始')

        _url = f'{baseUrl}/shipin/list-国产精品-{p}.html'
        rep = requests.get(_url, headers=headers)
        rep.encoding = 'utf8'
        soup = BeautifulSoup(rep.text, 'lxml')

        ass = soup.find_all(name='a',
                            attrs={'class': 'video-pic'})
        print(f'{name} 第 {p} 页 拉取完成')
        print(f'{name} 第 {p} 页 开始下载')
        index = 0
        for a in ass:

            print(f'{name} 第 {p} 页 第{index+1}段 开始读取')

            title = a.attrs['title']

            rep = requests.get(baseUrl +
                               a.attrs['href'], headers=headers)

            print(f'{name} 第 {p} 页 第{index+1}段 {title} 开始下载')

            filename = rootPath + sep + filterName(title) + '.mp4'

            if os.path.exists(filename):
                index += 1
                print(f'{name} {title} 文件已存在')
                continue

            bv = re.findall(r'(/common/gc/.*\.m3u8)', rep.text)
            if bv:
                mp4s = []
                bv = bv[0]
                url = f'https://s1.maomibf1.com{bv}'
                rep = requests.get(
                    url, headers=headers)

                _index = 0
                task_content = ''
                tasks = []
                for _url in rep.text.split('\n'):
                    if '.ts' not in _url:
                        continue
                    try:
                        mp4 = url .split('/')
                        mp4.pop()
                        mp4.append(_url)
                        mp4 = '/'.join(mp4)
                        _filename = rootPath + sep + \
                            filterName(title) + \
                            '_' + str(_index) + '.mp4'

                        t = threading.Thread(target=downloadFile,
                                             args=(mp4, _filename, headers))
                        t.setDaemon(True)
                        t.start()
                        tasks.append(t)

                        task_content += concatContent(_filename)
                        mp4s.append(_filename)
                        _index += 1
                    except BaseException:
                        pass
                for t in tasks:
                    t.join()
                writeConcatFile(task_content)
                try:
                    videoMerge(filename, title)
                except BaseException:
                    pass
                for path in mp4s:
                    os.remove(path)
            time.sleep(1)
            print(f'{name} 第 {p} 页 第{index+1}段 下载完成')
            index += 1
            '''

            rep.encoding = 'utf8'
            soup = BeautifulSoup(rep.text, 'lxml')

            mp4 = soup.find_all(name='input', attrs={'id': 'lin1k0'})[
                0].attrs['value']

            print(f'{name} 第 {p} 页 第{index+1}段 开始下载')
            print(mp4)

            if os.path.exists(filename):
                index += 1
                print(f'{name} 文件已存在')
                continue

            try:
                with requests.get(mp4, headers=headers, stream=True) as rep:
                    file_size = int(rep.headers['Content-Length'])
                    if rep.status_code != 200:
                        print(f'{name} 下载失败')
                        return False
                    label = '{:.2f}MB'.format(file_size / (1024 * 1024))
                    with click.progressbar(length=file_size, label=label) as progressbar:
                        with open(filename, "wb") as f:
                            for chunk in rep.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                                    progressbar.update(1024)
            except BaseException:
                pass
            '''
            time.sleep(1)
            print(f'{name} 第 {p} 页 第{index+1}段 下载完成')
            index += 1


datas = {
    'xiazai': 1,
    'tupian': 39,
    'shipin': 57,
    'guochan': 2,
}

funcs = {
    'xiazai': xiazai,
    'tupian': tupian,
    'shipin': shipin,
    'guochan': guochan,
}


def callback(name, p):
    if p <= datas[name]:
        return
    try:
        datas[name] = p
        with open('config/testimage.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(datas))
            f.close
    except BaseException:
        pass


def readConfig():
    global datas
    try:
        text = ''
        with open('config/testimage.json', 'r', encoding='utf-8') as f:
            text = f.read() or ''
            f.close
        print(text)
        if text:
            datas = json.loads(text)
    except BaseException:
        pass


def get(url: str, savepath: str = 'download', func=None) -> dict:

    savepath = 'F:'+sep+'资源下载'

    readConfig()

    fun = None
    p = 1
    name = ''

    for key in datas.keys():
        if key in url:
            name = key
            fun = funcs[name]
            p = datas[name]
            isnew = '0'
            if p > 1:
                isnew = input(f"检测到 {name} 之前读到了{p}页，1继续 0重新开始: ")
            if isnew == '0':
                p = 1
            break
    if fun:
        fun(savepath, name, p, callback)


if __name__ == "__main__":
    print(get(input("url: ")))
