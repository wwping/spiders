import requests
import re
import json
import os
import click
import threading
import shutil
import subprocess
import time
import math
sep = os.sep
# 需要依赖ffmpeg
# 有些资源会限速╭(╯^╰)╮
# 想下载大会员番剧或1080P+请填入大会员cookie到headers


class Bilibili:
    def __init__(self, ss, sessData='', savePath: str = 'download', func=None):
        self.ss = ss
        self.base_url = f"https://www.bilibili.com/bangumi/play/{ss}"
        self.headers = {
            "Referer": f"https://www.bilibili.com/bangumi/play/{ss}/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
            # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
            'Cookie': 'SESSDATA={}'.format(sessData),
        }
        savePath = savePath+sep+'番剧'
        self._savePath = savePath
        self.savePath = savePath + sep + ss + sep
        self.func = func
        self.func = func
        self.total = 0
        self.index = 0
        self.name = ''
        self.tasks = 0
        self.taskFile = self.savePath + 'task.txt'

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
        regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$)')
        space = re.compile(r'\s{2,}')
        return space.sub(" ", regexp.sub("", name))
    # 获取cid, bv_id, ep_id, 当前集数

    def get_params(self):
        rep = requests.get(self.base_url)
        name = re.findall(r'"name": "(.+?)",', rep.text)
        if not name:
            self.printMsg(f'\n{self.ss} 番号解析失败 ××××××××××××××××', color='err')
            return []
        name = self.filterName(name[0])

        config = re.findall(
            r'window.__INITIAL_STATE__=({.+?)]};', rep.text, re.S)[0] + ']}'
        epList = json.loads(config)['epList']

        self.savePath = self._savePath + sep + name + sep
        self.taskFile = self.savePath + 'task.txt'

        arr = []
        for ep in epList:
            arr.append({
                'name': self.filterName(f'{name} {ep["titleFormat"]} {ep["longTitle"]}'),
                'cid': ep['cid'],
                'bvid': ep['bvid'],
                'epid': ep['id'],
                'cover': 'https:' + ep['cover']
            })
        return arr

    def checkDir(self):
        try:
            os.makedirs(self.savePath + self.ss)
        except FileExistsError:
            pass
        # os.chdir(self.ss)

    def rmPiecesDir(self):
        try:
            shutil.rmtree(self.savePath + self.ss)
            os.remove(self.taskFile)
        except:
            pass
        else:
            pass

    def getFileByUrl(self, url, filename, title):

        self.printMsg(f"\n【{title}】 正在下载")
        pindex = 0

        with requests.get(url, headers=self.headers, stream=True) as rep:
            file_size = int(rep.headers['Content-Length'])
            if rep.status_code != 200:
                self.printMsg(f"\n【{title}】 下载失败", color='err')
                self.index += 1
                self.callback('data')
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
                            self.callback2(file_size, pindex, title=title)
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
                                self.callback2(file_size, pindex, title=title)

        self.printMsg(f"【{title}】 下载成功\n", color='success')
        self.printMsg(f"\n 休息一下", color='warn')
        self.index += 1
        self.callback('data', title=title)
        return True

    def getVideoFormat(self):
        return 'mp4'

    def concatContent(self, filename):
        content = "file '"+filename+"'\n"
        return content

    def writeConcatFile(self, content):
        with open(self.taskFile, 'w', encoding='utf-8') as f:
            f.write(content)
            f.close

    def videoMerge(self, taskFile, output, title=''):
        self.printMsg(f"\n【{title}】 分块视频合并中....................")
        self.callback('data', '合并中..')
        sentence = 'ffmpeg -loglevel error -f concat -safe 0 -i "{}" -c copy "{}.{}" -y'.format(
            taskFile, output, self.getVideoFormat())
        child = subprocess.Popen(sentence, shell=True)
        child.wait()
        self.printMsg(f"\n【{title}】 分块视频合并完成....................")

    def combineAV(self, videoFile, audioFile, output, title):
        self.printMsg(f"\n【{title}】 音频合并中....................")
        self.callback('data', '合并中..')
        sentence = 'ffmpeg -loglevel error -i "{}" -i "{}" -c copy "{}.{}" -y'.format(
            videoFile, audioFile, output, self.getVideoFormat())
        child = subprocess.Popen(sentence, shell=True)
        child.wait()
        self.printMsg(f"【{title}】 音频合并完成....................")

    def downloadPieces(self, data, title=''):

        if os.path.isfile(self.savePath +
                          title + "." + self.getVideoFormat()):
            self.printMsg('\n【' + self.savePath +
                          title + "." + self.getVideoFormat()+' 文件已存在', color='warn')
            self.index += len(data['result']['durl'])+1
            self.callback('data', title)
            self.tasks -= 1
            return True

        threads = []
        filepaths = []
        try:
            self.checkDir()
            task_content = ''
            for info in data['result']['durl']:
                filename = self.savePath + self.ss + sep + self.ss + '_' + title + \
                    '_' + str(info['order']) + "." + self.getVideoFormat()

                t = threading.Thread(target=self.getFileByUrl, args=(
                    info['url'], filename, title + ' 分块 ' + str(info['order'])))
                threads.append(t)
                t.setDaemon(True)
                t.start()

                filepaths.append(filename)

                task_content += self.concatContent(filename)

            for t in threads:
                t.join()

            if task_content != '':
                try:
                    self.writeConcatFile(task_content)
                    self.videoMerge(self.taskFile, self.savePath +
                                    title, title)
                except BaseException as e:
                    self.printMsg(f"{e}", color='err')
                    self.index += 1
                    self.callback('data')

        except BaseException:
            pass

        self.tasks -= 1
        for path in filepaths:
            os.remove(path)
        # self.rmPiecesDir()
        pass

    def downloadAudioAndVideo(self, text, item):

        if os.path.isfile(item["savePath"]):
            self.printMsg('\n【' + item["savePath"] +
                          '】 '+' 文件已存在', color='warn')
            self.index += 2
            self.callback('data')
            self.tasks -= 1
            return

        video = self.getFileByUrl(
            text['result']['dash']['video'][0]['base_url'], item['videoPath'], item['name'] + " 视频部分")

        audio = self.getFileByUrl(
            text['result']['dash']['audio'][0]['base_url'], item['audioPath'], item['name'] + " 音频部分")

        if video and audio:
            try:
                self.printMsg(f"\n【{item['name']}】 视频+音频 开始合并")
                self.callback('data', '合并中..')
                child = subprocess.Popen(
                    f'ffmpeg -loglevel error -i "{item["videoPath"]}" -i "{item["audioPath"]}" -vcodec copy -acodec copy "{item["savePath"]}" -y',  shell=True)
                child.wait()
                self.printMsg(f"【{item['name']}】 视频+音频 合并成功")
            except BaseException as e:
                self.printMsg(f"【{item['name']}】 {e}", color='err')
                pass

        try:
            os.remove(item['videoPath'])
            os.remove(item['audioPath'])
        except BaseException:
            pass

        self.tasks -= 1
        self.index += 1
        self.callback('data')
        # self.rmPiecesDir()

    def downCover(self, data, path, title):

        self.getFileByUrl(data, path, title)
        self.tasks -= 1

    def run(self):

        eplist = self.get_params()

        self.checkDir()
        self.total = 1
        self.index = 0
        self.callback('data', title='拉取数据中.')

        data = []
        for ep in eplist:
            rep = requests.get(f"https://api.bilibili.com/pgc/player/web/playurl?cid={ep['cid']}&qn=112&type=&otype=json&fourk=1&bvid={ep['bvid']}&ep_id={ep['epid']}&fnver=0&fnval=16&session=6665a83430e196a488e4786293452817",
                               headers=self.headers)
            text = json.loads(rep.text)
            if text['code'] == 0:
                item = {
                    'title': ep['name'],
                    'name': ep['name'],
                    'videoPath': self.savePath + ep['name'] + '_video.mp4',
                    'audioPath': self.savePath + ep['name'] + '_audio.mp3',
                    'savePath': self.savePath + ep['name'] + '.mp4',
                    'data': text
                }

                if ep['cover']:
                    self.total += 1
                    data.append({
                        'type': '3',
                        'path': self.savePath + ep['name'] + '.jpg',
                        'title':  ep['name'] + '封面',
                        'name': ep['name'],
                        'data': ep['cover']
                    })

                if('dash' in text['result'].keys()):
                    self.total += 3
                    data.append({
                        'type': '1',
                        'title':  ep['name'],
                        'name': ep['name'],
                        'videoPath': self.savePath + ep['name'] + '_video.mp4',
                        'audioPath': self.savePath + ep['name'] + '_audio.mp3',
                        'savePath': self.savePath + ep['name'] + '.mp4',
                        'data': text
                    })
                else:
                    self.total += len(text['result']['durl']) + 1
                    item['data'] = text
                    item['type'] = '2'
                    data.append({
                        'type': '2',
                        'title':  ep['name'],
                        'name': ep['name'],
                        'data': text
                    })

                self.printMsg(
                    f'{ep["name"]} 数据拉取成功√√√√√√√√√√√√√√√√√√√', color='success')
            else:
                self.printMsg(
                    f'{ep["name"]} 数据拉取失败：!!!!{text["message"]}!!!! ××××××××××××××××', color='err')

            self.callback('data', title='拉取数据...')
            self.printMsg(
                f'休息一下', color='warn')
            time.sleep(0.1)

        self.callback('data', title='开始下载...')

        '''
        length = len(data)-1

        _tasks = []

        while length >= 0:
            if self.tasks < 5:
                item = data[length]
                t = None
                if item['type'] == '1':
                    t = threading.Thread(
                        target=self.downloadAudioAndVideo, args=(item['data'], item))
                    t.setDaemon(True)
                    t.start()
                    _tasks.append(t)
                    # spawns.append(gevent.spawn(self.downloadAudioAndVideo, item['data'], item['item']))
                    # self.downloadAudioAndVideo(item['data'], item)
                elif item['type'] == '2':
                    # spawns.append(gevent.spawn(self.downloadPieces,item['data'], item['title']))
                    # self.downloadPieces(item['data'], item['title'])
                    t = threading.Thread(target=self.downloadPieces, args=(
                        item['data'], item['title']))
                    t.setDaemon(True)
                    t.start()
                    _tasks.append(t)
                elif item['type'] == '3':
                    # spawns.append(gevent.spawn(self.getFileByUrl,item['data'], item['path'], item['title']))
                    # self.getFileByUrl(item['data'], item['path'], item['title'])
                    t = threading.Thread(target=self.downCover, args=(
                        item['data'], item['path'], item['title']))
                    t.setDaemon(True)
                    t.start()
                    _tasks.append(t)
                self.tasks += 1
                length -= 1
            else:
                time.sleep(0.1)

        for t in _tasks:
            t.join()
        '''

        for item in data:
            if item['type'] == '1':
                # spawns.append(gevent.spawn(self.downloadAudioAndVideo, item['data'], item['item']))
                self.downloadAudioAndVideo(item['data'], item)
            elif item['type'] == '2':
                # spawns.append(gevent.spawn(self.downloadPieces,item['data'], item['title']))
                self.downloadPieces(item['data'], item['title'])
            elif item['type'] == '3':
                # spawns.append(gevent.spawn(self.getFileByUrl,item['data'], item['path'], item['title']))
                self.getFileByUrl(item['data'], item['path'], item['title'])

        self.rmPiecesDir()


def get(url: str, savepath: str = 'download', func=None, sessData: str = '') -> dict:
    bv = re.findall(r'(BV[0-9a-zA-Z]*)', url)
    ss = re.findall(r'play/(ss[0-9a-zA-Z]*)', url)
    ep = re.findall(r'play/(ep[0-9a-zA-Z]*)', url)

    bv = bv or ss or ep
    if bv:
        bv = bv[0]
        tool = Bilibili(bv, sessData,
                        savepath, func=func)
        tool.name = url
        tool.run()
    else:
        self.printMsg('\n解析失败', color='err')

    data = {}
    data["imgs"] = []
    data["videos"] = []
    data["m4s"] = []
    return data
