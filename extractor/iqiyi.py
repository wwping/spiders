import requests
import re
import json
import asyncio
import urllib3
import os
import shutil
import click
import subprocess
import time
import math
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from browsermobproxy import Server


urllib3.disable_warnings()
sep = os.sep
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)


class Iqiyi:
    def __init__(self, func=None):

        self.taskFile = ''
        self.savepath = ''
        self.name = ''
        self.func = func
        self.total = 0
        self.index = 0
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q = 0.9',
            'referer': '',
            'Cookie': 'UM_distinctid=17241b11bb457-02d9476df7f82b-7373667-1fa400-17241b11bb5b14; CNZZDATA1278736628=1181878469-1590239181-null%7C1590239181',
        }

    def callback(self, typeName, title=None):
        if self.func:
            self.func({
                'type': 'data',
                'name': self.name,
                'total': self.total,
                'index': self.index,
                'title': title,
            })

    def callback2(self, total, index, title=None):
        if index > total:
            index = total
        if self.func:
            self.func({
                'type': 'progress',
                'name': self.name,
                'total': total,
                'index': index,
                'title': title,
            })

    def callbackMsg(self, msg, color=None):
        if self.func:
            self.func({
                'type': 'msg',
                'msg': msg,
                'color': color,
            })

    def printMsg(self, msg, color=None):
        if self.func:
            self.callbackMsg(msg, color)
        else:
            print(msg)

    def filterName(self, name):
        regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$|\u2027)')
        space = re.compile(r'\s{2,}')
        return space.sub(" ", regexp.sub("", name))
        # return re.subn('[^0-9a-zA-Z\u4e00-\u9fa5\-_\s]', '', name)[0]

    def checkDir(self, path=''):
        """
        检查文件夹是否存在，存在返回True;不存在则创建，返回False
        """
        _path = path or self.savepath
        if not os.path.exists(_path):
            os.makedirs(_path)
            return False
        return True

    def getVideoFormat(self):
        return 'mp4'
        if 'flv' in self.data['data']['format']:
            return 'flv'
        else:
            if 'mp4' in self.data['data']['format']:
                return 'mp4'

    def concatContent(self, filename):
        content = "file '"+filename+"'\n"
        return content

    def writeConcatFile(self, content):
        with open(self.taskFile, 'w', encoding='utf-8') as f:
            f.write(content)
            f.close

    def videoMerge(self, taskFile, output, title=''):
        self.printMsg(f"\n【{title}】 视频合并中....................")
        sentence = 'ffmpeg -loglevel error -f concat -safe 0 -i "{}" -c copy "{}" -y'.format(
            taskFile, output)
        child = subprocess.Popen(sentence, shell=True)
        child.wait()
        self.printMsg(f"\n【{title}】 视频合并完成....................")

    def getFileByUrl(self, url, filename, title):

        self.printMsg(f"\n【{title}】 正在下载")
        pindex = 0

        if os.path.isfile(filename):
            self.printMsg('【' + filename + '】 '+' 文件已存在', color='warn')
            self.index += 1
            self.callback('data', title)
            return

        dindex = 0

        while dindex < 10:
            try:
                with requests.get(url, headers={}) as rep:
                    file_size = int(rep.headers['Content-Length'])
                    if rep.status_code != 200:
                        self.printMsg(f"\n【{title}】 下载失败", color='err')
                        self.index += 1
                        self.callback('data', title)
                        return False

                    if os.path.isfile(filename):
                        fsize = os.path.getsize(filename)
                        if abs(fsize-file_size) < 500:
                            self.printMsg('\n【' + filename +
                                          '】 '+' 文件已存在', color='warn')
                            self.index += 1
                            self.callback('data', title)
                            return True

                    label = '{:.2f}MB'.format(file_size / (1024 * 1024))
                    if self.func:
                        with open(filename, "wb") as f:
                            for chunk in rep.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                                    pindex += 1027
                                    if pindex > file_size:
                                        pindex = file_size
                                    self.callback2(
                                        file_size, pindex, title=title)
                    else:
                        with click.progressbar(length=file_size, label=label) as progressbar:
                            with open(filename, "wb") as f:
                                for chunk in rep.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                                        progressbar.update(1024)
                                        pindex += 1027
                                        if pindex > file_size:
                                            pindex = file_size
                                        self.callback2(
                                            file_size, pindex, title=title)
                break
            except BaseException:
                dindex += 1
                time.sleep(3)

        self.printMsg(f"【{title}】 下载成功", color='success')

        self.printMsg(f"\n 休息一下", color='warn')
        time.sleep(0.5)
        self.index += 1
        self.callback('data', title=title)
        return True

    def run(self, url):

        self.checkDir()
        self.total = 1
        self.index = 0

        self.callback('data', title='拉取数据')
        rep = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
            'Host': url.split('/')[2]
        })
        title = re.findall('name="irTitle" content="(.*)" />', rep.text)[0]

        baseUrl = "http://jiexi.380k.com/?url=" + url

        server = None
        driver = None
        try:
            server = Server("browsermob-proxy\\bin\\browsermob-proxy.bat")
            server.start()
            proxy = server.create_proxy()

            option = ChromeOptions()
            option.add_argument('--proxy-server={0}'.format(proxy.proxy))

            option.add_argument('headless')  # 设置option
            option.add_experimental_option(
                'excludeSwitches', ['enable-automation'])
            option.add_argument('--ignore-certificate-errors')
            driver = Chrome(options=option)

            proxy.new_har("ht_list2", options={'captureContent': True})

            driver.get(baseUrl)

            time.sleep(10)

            result = proxy.har
        except BaseException as e:
            server.stop()
            if driver:
                driver.quit()
            print(e)
            self.printMsg("拉取数据失败", color="err")
            self.callback('data', title='拉取数据失败')
            return

        m3u8 = None

        for entry in result['log']['entries']:
            if '.m3u8' in entry['request']['url']:
                m3u8 = entry['request']['url']

        server.stop()
        if driver:
            driver.quit()

        videos = []

        try:
            rep = requests.get(m3u8, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
                'Host': m3u8.split('/')[2],
                'Referer': m3u8.split('/')[2]
            })
            for filename in rep.text.split('\n'):
                if '.ts?' in filename:
                    videos.append(filename)
        except BaseException:
            self.printMsg("拉取数据失败", color="err")
            self.callback('data', title='拉取数据失败')
            return

        self.total = len(videos)
        self.index = 0
        self.callback('data', title='拉取数据成功')
        self.callback('data', title='准备下载')

        index = 0
        taskContent = ""
        tempPath = self.savepath + sep + title
        self.checkDir(tempPath)
        output = self.savepath + sep + title + '.' + self.getVideoFormat()
        for url in videos:
            filename = tempPath + sep + \
                str(index) + '.' + self.getVideoFormat()
            taskContent += self.concatContent(filename)
            self.getFileByUrl(url, filename, title + '_' + str(index))
            index += 1
            self.writeConcatFile(taskContent)

        self.videoMerge(self.taskFile, output, title)

        try:
            shutil.rmtree(tempPath)
            os.remove(self.taskFile)
        except BaseException:
            pass

        self.callback('data')


def get(url: str, savepath: str = 'download', func=None) -> dict:
    mgtv = Iqiyi(func=func)

    mgtv.taskFile = savepath + sep + 'taskfile.txt'
    mgtv.savepath = savepath
    mgtv.name = url

    mgtv.run(url)

    data = {}
    data["imgs"] = []
    data["videos"] = []
    data["m4s"] = []
    return data


if __name__ == "__main__":
    get(url='https://www.iqiyi.com/v_19ry8g1ngc.html')
