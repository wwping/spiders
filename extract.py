import re
from prettytable import PrettyTable
from requests.exceptions import ConnectTimeout, ConnectionError
from utils import download
import pyperclip
import time
import re
import os
import json
import signal
import threading
import tkinter
from extractor import (acfun, baidutieba, bilibili, changya, douyin, haokan,
                       ku6, kuaishou, kugou, kuwo, lizhiFM, lofter, music163,
                       open163, pearvideo, pipigaoxiao, pipix, qianqian,
                       qingshipin, qqmusic, quanminkge, qutoutiao, sing5,
                       sohuTV, ted, tudou, wechat_article_cover, weibo, weishi,
                       xiaokaxiu, xinpianchang, zhihu_video, zuiyou_voice, tuchong, meizi, testimage, pcav, zzzttt)

funcMap = {
    'douyin': douyin,
    '5sing': sing5,
    'kugou': kugou,
    'acfun': acfun,
    'bilibili': bilibili,
    'pipix': pipix,
    'kuwo': kuwo,
    'ku6': ku6,
    'haokan': haokan,
    'music.163': music163,
    'y.qq': qqmusic,
    'mzitu': meizi,
    'stats.gov': pcav,
    'qke866': testimage,
    'zzzttt': zzzttt
}

if not os.path.exists('config'):
    os.makedirs('config')

showinfo = '''

    请在 config.json 文件配置下载路径

    输入内容包含完整url链接的内容即可，自动提取
    - 抖音视频分享链接   https://v.douyin.com/w3G93b/
    - bilibili视频,番剧链接   https://www.bilibili.com/video/BV1mp4y1X7sr
    - acfun视频链接  https://www.acfun.cn/v/ac15179107
    - 5sing音乐链接 http://5sing.kugou.com/fc/17457264.html
    # hash=86B0B6CCBE1341065931558886E4C07F&album_id=37236081
    - 酷狗音乐链接 https://www.kugou.com/song/
    - 酷我音乐链接 http://www.kuwo.cn/play_detail/1850233
    - 酷6视频  https://www.lizhi.fm/1244717/2587320075826653702
    - 好看视频 https://haokan.baidu.com/v?vid=10046831123777078980&tab=recommend
    - 网易云音乐 https://music.163.com/#/song?id=5266159
    - QQ音乐 分享链接 https://c.y.qq.com/base/fcgi-bin/u?__=eawrb35

    如果需要下载 bilibili 高画质视频，请自行设置 sessData
    sessData用于判断登录状态和是否会员，网页登录BiliBili后，按F12 Application中cookie可以找到
    '''


'''
    已经下载的一些url的缓存用来判断是否下载过
'''
downloadCache = []

'''
    剪贴板
'''
clipUrls = []
clipData = ''


def readUrls(text):
    res = []

    text = text.replace('\n', '杠嗯杠嗯').replace(' ', '')
    urls = re.findall(
        r"https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]\.[-A-Za-z]+[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", text)

    if urls:
        for idx, url in enumerate(urls):
            for key in funcMap:
                if(key in url):
                    res.append(url)
                    break

    return res


def listenerClip():
    '''
        读取剪贴板
    '''
    global clipData

    while 1:
        jiantieban = pyperclip.paste() or ''
        if jiantieban != clipData:
            clipData = jiantieban
            urls = readUrls(clipData)
            if urls:
                for url in urls:
                    if url in clipUrls:
                        continue
                    clipUrls.append(url)
                    print(f'\n\n收到剪贴板的url:{url}\n')
                writeClip(clipUrls)

        time.sleep(0.1)


def signal_handler(signal, frame):
    exit()


signal.signal(signal.SIGINT, signal_handler)


def writeClip(data):
    with open('config/clips.txt', 'w') as f:
        f.write('\n'.join(data))
        f.close


def readClip():
    data = ''
    if os.path.exists('config/clips.txt'):
        with open('config/clips.txt', 'r', encoding='utf-8') as f:
            data = f.read() or ''
            f.close

    return readUrls(data)


clipUrls = readClip()


def readByClip():
    global clipUrls
    if len(clipUrls) > 0:
        rclip = input("\n####剪贴板存在"+str(len(clipUrls)
                                        )+" 条url，是否处理 0跳过 1处理 2清除>>")
        if rclip == '1':
            while len(clipUrls) > 0:
                _url = clipUrls.pop(0)
                print(f"\n正在解析链接【{_url}】")
                spider(_url)
                print()
                writeClip(clipUrls)
        elif rclip == '2':
            clipUrls = []
            writeClip(clipUrls)


def readConfig():
    with open('config/config.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read() or '{}')
        f.close
    return data


config = readConfig()
sessData = config.get('sessData') or ''
downloadPath = config.get('downloadPath') or 'download'
if not os.path.exists(downloadPath):
    try:
        os.makedirs(downloadPath)
    except BaseException:
        print('目录创建失败，请在config.json配置一个正确的目录')
        exit()
downloadPaths = config.get('downloadPaths') or {}
isInput = config.get('isInput') or '0'
isClip = config.get('isClip') or '0'


def filterName(name):
    regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$)')
    space = re.compile(r'\s{2,}')
    return space.sub(" ", regexp.sub("", name))
    # return re.subn('[^0-9a-zA-Z\u4e00-\u9fa5\-_\s]', '', name)[0]


def spiderUrl(text):
    '''
        匹配url 然后去读取
    '''
    if not text:
        return
    urls = re.findall(
        r"https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]\.[-A-Za-z]+[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", text)
    if not urls:
        return
    for idx, url in enumerate(urls):
        print(f"\n正在解析链接【{url}】")
        spider(url)
        print()
        try:
            clipUrls.remove(url)
        except BaseException:
            pass


def get(url=None):
    if url is None:
        url = input("请输入链接：")
    f = None
    for key in funcMap:
        if(key in url):

            path = f'{downloadPath}\\{key}'

            print(f"###下载路径为:{path}")

            if key == 'bilibili':
                data = bilibili.get(url, savepath=path, sessData=sessData)
                return {}
            else:
                f = funcMap[key]
                data = f.get(url)
                data['pathname'] = path
                return data

    return {"msg": "链接无法解析"}


def spider(url):
    data = get(url)

    text = data.get("text")
    msg = data.get("msg")
    if msg or text:
        print(msg or text)
        print()
        return

    title = data.get("title")
    audioName = data.get("audioName")
    videoName = data.get("videoName")
    imgs = data.get("imgs")
    audios = data.get("audios")
    videos = data.get("videos")
    pathName = data.get('pathname')
    m4s = data.get('m4s')

    file_name = (audioName or videoName or title or None)
    savePath = pathName

    downs = [
        {'type': 'jpg', 'data': imgs or []},
        {'type': 'mp3', 'data': audios or []},
        {'type': 'mp4', 'data': videos or []},
        {'type': 'm4s', 'data': m4s or []},
    ]

    for v in downs:
        for vv in v['data']:
            url = vv
            print(url)
            if not isinstance(vv, str):
                if vv['name']:
                    file_name = filterName(vv['name'])
                url = vv['url']
            download(url, file_name=file_name,
                     file_type=v['type'], save_path=savePath)


if __name__ == "__main__":

    if isInput == '0':
        print("\n####正在监听剪贴板,复制视频连接即可自动下载>>\n")

    '''
    elif isClip == '1':
        t1 = threading.Thread(target=listenerClip)
        t1.setDaemon(True)
        t1.start()
    '''
    what = ''

    while True:
        try:
            '''
                从剪贴板自动读取
            '''
            if isInput == '0':
                text = pyperclip.paste()
                if what == text:
                    time.sleep(1)
                    continue
                what = text
            '''
                从剪贴板读取
            '''
            # readByClip()

            '''
                手动输入
            '''
            if isInput == '1':
                # os.system('cls')
                print(showinfo)
                what = input("\n####输入包含url链接的内容 cls清屏>>")
                if what == 'cls':
                    os.system('cls')
                    continue
            '''
                去匹配url
            '''
            spiderUrl(what)

            if isInput == '0':
                # os.system('cls')
                print(showinfo)
                print("\n####正在监听剪贴板,复制视频连接即可自动下载>>\n")

        except RuntimeError:
            print("运行超时")
        except ConnectTimeout:
            print("网络连接超时")
        except ConnectionError:
            print("连接错误")
