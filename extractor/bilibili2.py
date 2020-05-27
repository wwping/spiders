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

urllib3.disable_warnings()
sep = os.sep
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)


class Bilibili:
    def __init__(self, bvId, sessData='', quality=64, func=None):

        self.bvId = bvId
        # sessData用于判断登录状态和是否会员，网页登录BiliBili后，按F12 Application中cookie可以找到
        self.sessData = sessData
        # quality
        # 116: 高清1080P60 (需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频)
        # 112: 高清1080P+ (hdflv2) (需要大会员)
        # 80: 高清1080P (flv)
        # 74: 高清720P60 (需要大会员)
        # 64: 高清720P (flv720)
        # 32: 清晰480P (flv480)
        # 16: 流畅360P (flv360)
        self.name = ''
        self.quality = quality
        self.pages = []
        self.cid = 0
        self.bvDir = script_dir + sep + 'video' + sep + self.bvId + sep
        self.piecesDir = self.bvDir + 'pieces' + sep
        self.taskFile = self.piecesDir + 'task.txt'
        self.base_url = 'https://www.bilibili.com/video/' + self.bvId
        self._savepath = self.bvDir
        self.func = func
        self.total = 0
        self.index = 0
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q = 0.9',
            # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
            'Cookie': 'SESSDATA={}'.format(self.sessData),
        }

    # 请求视频下载地址时需要添加的请求头
        self.download_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'Referer': 'https://www.bilibili.com/video/' + self.bvId,
            'Origin': 'https://www.bilibili.com',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8'
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

    def getCid(self):
        # cidUrl = 'https://api.bilibili.com/x/player/pagelist?bvid=' + self.bvId
        cidUrl = 'https://api.bilibili.com/x/web-interface/view?bvid=' + self.bvId
        html = requests.get(cidUrl, headers=self.base_headers).json()
        self.info = html['data']
        self.info['title'] = self.filterName(self.info['title'])
        self.cid = html['data']['cid']
        self.pages = html['data']['pages']

        self.bvDir = self._savepath + sep + \
            '视频' + sep + self.info['title'] + sep
        self.piecesDir = self.bvDir + 'pieces' + sep
        self.taskFile = self.piecesDir + 'task.txt'

    def getResponseData(self, _cid):
        cid = _cid or self.cid
        playUrl = 'https://api.bilibili.com/x/player/playurl?cid={}&bvid={}&qn={}&type=&otype=json&fourk=1&fnver=0&fnval=16'.format(
            cid, self.bvId, self.quality)
        data = requests.get(playUrl, headers=self.base_headers).json()
        return data

    def mkPiecesDir(self):
        """
        检查文件夹是否存在，存在返回True;不存在则创建，返回False
        """
        if not os.path.exists(self.piecesDir):
            os.makedirs(self.piecesDir)
            return False
        return True

    def rmPiecesDir(self):
        try:
            shutil.rmtree(self.piecesDir)
            os.remove(self.taskFile)
        except:
            pass
        else:
            pass

    def getVideoFormat(self):
        return 'mp4'
        if 'flv' in self.data['data']['format']:
            return 'flv'
        else:
            if 'mp4' in self.data['data']['format']:
                return 'mp4'

    def concatContent(self, filename):
        content = "file '"+self.piecesDir+filename+"'\n"
        return content

    def writeConcatFile(self, content):
        with open(self.taskFile, 'w', encoding='utf-8') as f:
            f.write(content)
            f.close

    def videoMerge(self, taskFile, output, title=''):
        self.printMsg(f"\n【{title}】 视频合并中....................")
        sentence = 'ffmpeg -loglevel error -f concat -safe 0 -i "{}" -c copy "{}.{}" -y'.format(
            taskFile, output, self.getVideoFormat())
        child = subprocess.Popen(sentence, shell=True)
        child.wait()
        self.printMsg(f"\n【{title}】 视频合并完成....................")

    def combineAV(self, videoFile, audioFile, output, title):
        self.printMsg(f"\n【{title}】 音频合并中....................")
        sentence = 'ffmpeg -loglevel error -i "{}" -i "{}" -c copy "{}.{}" -y'.format(
            videoFile, audioFile, output, self.getVideoFormat())
        child = subprocess.Popen(sentence, shell=True)
        child.wait()
        self.printMsg(f"【{title}】 音频合并完成....................")

    def getFileByUrl(self, url, filename, title):

        self.printMsg(f"\n【{title}】 正在下载")
        pindex = 0

        with requests.get(url, headers=self.download_headers, stream=True) as rep:
            file_size = int(rep.headers['Content-Length'])
            if rep.status_code != 200:
                self.printMsg(f"\n【{title}】 下载失败", color='err')
                self.index += 1
                self.callback('data', title)
                return False
            label = '{:.2f}MB'.format(file_size / (1024 * 1024))
            if self.func:
                with open(self.piecesDir + filename, "wb") as f:
                    for chunk in rep.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            pindex += 1027
                            if pindex > file_size:
                                pindex = file_size
                            self.callback2(file_size, pindex, title=title)
            else:
                with click.progressbar(length=file_size, label=label) as progressbar:
                    with open(self.piecesDir + filename, "wb") as f:
                        for chunk in rep.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                progressbar.update(1024)
                                pindex += 1027
                                if pindex > file_size:
                                    pindex = file_size
                                self.callback2(file_size, pindex, title=title)

        self.printMsg(f"【{title}】 下载成功", color='success')

        self.printMsg(f"\n 休息一下", color='warn')
        time.sleep(1)
        self.index += 1
        self.callback('data', title=title)
        return True

    def downloadCover(self, url, filename, title=''):

        if os.path.isfile(self.bvDir + filename):
            self.printMsg('\n【' + self.bvDir + filename +
                          '】 '+' 文件已存在', color='warn')
            self.index += 1
            return True

        self.printMsg(f"\n【{title}】封面下载中 ....")

        pindex = 0
        with requests.get(url, headers=self.download_headers, stream=True) as rep:
            file_size = int(rep.headers['Content-Length'])
            self.callback2(file_size, 0, title=title)
            if rep.status_code != 200:
                self.printMsg(f"【{title}】封面下载失败 ...", color='err')
                return False
            label = '{:.2f}MB'.format(file_size / (1024 * 1024))
            if self.func:
                with open(self.bvDir + filename, "wb") as f:
                    for chunk in rep.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            pindex += 1024
                            if pindex > file_size:
                                pindex = file_size
                            self.callback2(file_size, pindex, title=title)
            else:
                with click.progressbar(length=file_size, label=label) as progressbar:
                    with open(self.bvDir + filename, "wb") as f:
                        for chunk in rep.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                progressbar.update(1024)
                                pindex += 1024
                                self.callback2(file_size, pindex, title=title)

            self.index += 1
            self.callback('data', title)
            self.printMsg(f"【{title}】封面下载成功....", color='success')
            return True

        pass

    def downloadPieces(self, data, _title):
        title = _title or self.info['title']

        output = self.bvDir + title

        if os.path.isfile(output + '.'+self.getVideoFormat()):
            self.printMsg('\n【' + output + '.' +
                          self.getVideoFormat() + '】 '+' 文件已存在', color='warn')
            self.index += len(data['data']['durl'])+1
            self.callback('data', title)
            return True

        self.mkPiecesDir()
        task_content = ''
        for info in data['data']['durl']:
            filename = title + '_' + str(info['order']) + '.mp4'
            task_content += self.concatContent(filename)
            self.getFileByUrl(
                info['url'], filename, title)
        self.writeConcatFile(task_content)
        self.videoMerge(self.taskFile, output, title)
        self.rmPiecesDir()
        self.index += 1
        self.callback('data', title)
        pass

    def downloadAudioAndVideo(self, data, _title):
        self.mkPiecesDir()
        filename = self.bvId + '.mp4'
        audioFilename = self.bvId + '_audio.mp4'
        title = _title or self.info['title']

        output = self.bvDir+title

        if os.path.isfile(output + '.'+self.getVideoFormat()):
            self.printMsg('【' + output + '.' +
                          self.getVideoFormat() + '】 '+' 文件已存在', color='warn')
            self.index += 3
            self.callback('data', title)
        else:
            self.getFileByUrl(
                data['data']['dash']['audio'][0]['baseUrl'], audioFilename, title + ' 音频部分')

            url = None

            for info in data['data']['dash']['video']:
                if info['id'] == self.quality:
                    url = info['baseUrl']
                    break

            if not url:
                url = data['data']['dash']['video'][0]['baseUrl']

            self.getFileByUrl(
                info['baseUrl'], filename, title + ' 视频部分')

            self.combineAV(self.piecesDir+filename, self.piecesDir +
                           audioFilename, output, title)
            self.index += 1
            self.callback('data', title)

        self.rmPiecesDir()
        pass

    def run(self):

        self.getCid()
        self.mkPiecesDir()
        pic = self.info.get('pic')

        self.total = 0
        self.index = 0
        if pic:
            self.total += 1

        self.callback('data', title='拉取数据')

        data = []
        for page in self.pages:
            title = f"{self.info['title']} P{str(page['page'])} {page['part']}"
            title = self.filterName(title)

            _data = self.getResponseData(page['cid'])
            if _data['code'] == 0:
                if('dash' in _data['data'].keys()):
                    self.total += 3
                    data.append({
                        'type': '1',
                        'title': title,
                        'data': _data
                    })
                else:
                    self.total += len(_data['data']['durl']) + 1
                    data.append({
                        'type': '2',
                        'title': title,
                        'data': _data
                    })
                self.printMsg(f"【{title}】 数据拉取成功....", color='success')
            else:
                self.printMsg(
                    f'{title} 数据拉取失败：!!!!{text["message"]}!!!! ××××××××××××××××', color='err')
            self.printMsg(
                f'休息一下', color='warn')
            time.sleep(1)

        self.callback('data')

        if pic:
            self.downloadCover(pic, self.info.get(
                'title') + '.jpg', self.info['title'])

        for item in data:
            self.data = item
            if item['type'] == '1':
                self.downloadAudioAndVideo(item['data'], item['title'])
            else:
                self.downloadPieces(item['data'], item['title'])

        self.rmPiecesDir()


def get(url: str, savepath: str = 'download', func=None, sessData: str = '') -> dict:
    bv = re.findall(r'video/(BV[0-9a-zA-Z]*)', url)
    if bv:
        bv = bv[0]
        tool = Bilibili(bv, sessData, 116, func=func)
        tool._savepath = savepath
        tool.bvDir = savepath + sep + tool.bvId + sep
        tool.piecesDir = tool.bvDir + 'pieces' + sep
        tool.taskFile = tool.piecesDir + 'task.txt'
        tool.name = url
        tool.run()

    data = {}
    data["imgs"] = []
    data["videos"] = []
    data["m4s"] = []
    return data
