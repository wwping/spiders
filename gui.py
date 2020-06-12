
import re
from prettytable import PrettyTable
from requests.exceptions import ConnectTimeout, ConnectionError
from utils import download
from cover import Cover
from change import Change
import pyperclip
import time
import re
import os
import json
import signal
import threading
import tkinter
import tkinter.font as tf
from tkinter.filedialog import askdirectory
from tkinter import(Menu, Frame, LabelFrame, Message, messagebox,
                    Text, Entry, Button, ttk, Label, scrolledtext, INSERT, END, BOTH, LEFT, RIGHT, Checkbutton, IntVar, StringVar)

from extractor import (acfun, baidutieba, bilibili, changya, douyin, haokan,
                       ku6, kuaishou, kugou, kuwo, lizhiFM, lofter, music163,
                       open163, pearvideo, pipigaoxiao, pipix, qianqian,
                       qingshipin, qqmusic, quanminkge, qutoutiao, sing5,
                       sohuTV, ted, tudou, wechat_article_cover, weibo, weishi,
                       xiaokaxiu, xinpianchang, zhihu_video, zuiyou_voice, tuchong, mgtv, iqiyi, qqtv)

sep = os.sep

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
    'mgtv': mgtv,
    'iqiyi': iqiyi,
    'v.qq': qqtv
}

if not os.path.exists('config'):
    os.makedirs('config')

showinfo = '''
请在 config.json 文件配置下载路径

输入内容包含完整url链接的内容即可，自动提取

- 抖音视频分享链接   
https://v.douyin.com/w3G93b/
- bilibili视频,番剧链接   
https://www.bilibili.com/video/BV1mp4y1X7sr
- acfun视频链接  
https://www.acfun.cn/v/ac15179107
- 5sing音乐链接 
http://5sing.kugou.com/fc/17457264.html#hash=86B0B6CCBE1341065931558886E4C07F&album_id=37236081
- 酷狗音乐链接 
https://www.kugou.com/song/
- 酷我音乐链接 
http://www.kuwo.cn/play_detail/1850233
- 酷6视频  
https://www.lizhi.fm/1244717/2587320075826653702
- 好看视频 
https://haokan.baidu.com/v?vid=10046831123777078980&tab=recommend
- 网易云音乐 
https://music.163.com/#/song?id=5266159
- QQ音乐 分享链接 
https://c.y.qq.com/base/fcgi-bin/u?__=eawrb35

    如果需要下载 bilibili 高画质视频，请自行设置 sessData
    sessData用于判断登录状态和是否会员，网页登录BiliBili后，按F12 Application中cookie可以找到
    '''
'''
'name': url,
'index': 1,
'total': 1,
'item_index': 1,
'item_total': 1,
'title': '',
'done': False
'''
progress = []
waiting = []

'''
主窗口
'''
top = tkinter.Tk()
top.title('下载器')
w = 1000
h = 500
ws = top.winfo_screenwidth()
hs = top.winfo_screenheight()
# 计算 x, y 位置
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
top.geometry('%dx%d+%d+%d' % (w, h, x, 100))

'''
菜单
'''


def runCover():
    top.iconify()
    Cover()


def runChange():
    top.iconify()
    Change()


menubar = Menu(top)
menubar.add_command(label="生成封面", command=runCover)
menubar.add_command(label="转码", command=runChange)
top['menu'] = menubar
'''
布局
'''
frmLeft = LabelFrame(width=300, height=100, text='状态', labelanchor='nw')
frmSelectPath = Frame(width=100, height=100)
frmTop = Frame(width=100, height=100)
frmBottom = LabelFrame(width=500, text='下载列表', height=400)

frmLeft.pack(side='left', fill='y', padx='5', pady='5')
frmSelectPath.pack(side='top', fill='x', padx='5', pady='5')
frmTop.pack(side='top', fill='x', padx='5', pady='5')
frmBottom.pack(side='right', fill=BOTH, expand='yes', padx='5', pady='5')

'''
控件
'''
clupValue = IntVar()
clipButton = Checkbutton(frmLeft, text="剪贴板",
                         onvalue=1, offvalue=0, height=1, variable=clupValue)
clipButton.pack(side='top', expand='no', fill=None)


def showinfoEvent():
    messagebox.showinfo('提示', showinfo)


inputText = scrolledtext.ScrolledText(frmLeft, bd=0, width=50, bg=None)
inputText.pack(side='left', fill='y', expand='no')

message = Button(frmSelectPath, bd=1, bg=None,
                 text='支持哪些??', command=showinfoEvent)
message.pack(side='left', fill=None, expand='no')

selectPathLabel = Label(frmSelectPath, text="保存路径文件夹:")
selectPathLabel.pack(side="left")
downloadPath = StringVar(top, value='download')
inputSelectPath = Entry(frmSelectPath, bd=0,
                        textvariable=downloadPath, state='readonly')
inputSelectPath.pack(side="left", fill="x", expand='yes')


def selectPath():
    path_ = askdirectory()
    if path_ and os.path.exists(path_):
        downloadPath.set(path_.replace('/', sep).replace('\\', sep))
        writeConfig()


def openPath():
    os.system(f'start explorer {downloadPath.get()}')


Button(frmSelectPath, bd=1, bg=None,
       text='打开文件夹', command=openPath).pack(side='right')

Button(frmSelectPath, bd=1, bg=None,
       text='选择文件夹', command=selectPath).pack(side='right')


inputLabel = Label(frmTop, text="输入带url的内容:")
inputLabel.pack(side="left")

inputUrlValue = StringVar()
inputUrl = Entry(frmTop, bd=0, textvariable=inputUrlValue)
inputUrl.pack(side="left", fill="x", expand='yes')


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


def readUrlCallBack():
    '''
        匹配url 然后去读取
    '''
    urls = readUrls(inputUrlValue.get())
    inputUrlValue.set('')
    if not urls:
        return
    for url in urls:
        appendWaiting(url)


inputBtn = Button(frmTop, bd=1, text="开始解析>>>", command=readUrlCallBack)
inputBtn.pack()

'''
表格
'''
columns = ("名称", '大小', '状态', '任务', "进度")
treeview = ttk.Treeview(frmBottom, height=18, background=None, foreground=None,
                        show="headings", columns=columns)  # 表格

for i in columns:
    treeview.column(i, width=100, anchor='center')  # 表示列,不显示
    treeview.heading(i, text=i)  # 显示表头


treeview.pack(side='left', fill='both', expand='yes')

scroll1 = ttk.Scrollbar(frmBottom, orient='vertical', command=treeview.yview)
scroll1.place(relx=0.971, rely=0.028, relwidth=0.024, relheight=0.958)
treeview.configure(yscrollcommand=scroll1.set)


def reloadTreeview():
    for _ in map(treeview.delete, treeview.get_children("")):
        pass
    index = 0
    for item in progress:
        title = item.get('title')
        status = '下载中'

        total = '{:.2f}MB'.format(item['total'] / 1024/1024)
        if total == 0:
            _progress = '0%'
        else:
            _progress = '{:.2f}%'.format(
                item['index'] / item['total'] * 100)
        itemIndex = ''
        if item["item_total"] == 0:
            itemIndex = '0/0'
        else:
            itemIndex = f'{item["item_index"]}/{item["item_total"]}'

        treeview.insert('', index, values=(title,
                                           total, status, itemIndex, _progress))
        index += 1

    for item in waiting:
        treeview.insert('', index, values=('',
                                           0, '0/0', '等待中', '0%'))
        index += 1
    treeview.after(30, reloadTreeview)


reloadTreeview()

# 方法
'''
'name': url,
'index': 1,
'total': 1,
'item_index': 1,
'item_total': 1,
'title': '',
'done': False
'''

# 添加到等待下载

clipCaches = []


def appendWaiting(url):
    if url in waiting:
        return False

    waiting.append(url)
    appendClip(url)


# 添加到下载


def appendProgress(url):
    index = -1

    for idx, item in enumerate(progress):
        _name = item.get('name')
        if _name == url:
            index = idx
    if index == -1:
        progress.append({
            'name': url,
            'index': 1,
            'total': 1,
            'item_index': 1,
            'item_total': 1,
            'title': '',
            'done': False
        })
        spider(callbackFunc, url)

# 输出文字状态信息


colorNames = ['err', 'warn', 'default', 'success', 'info']
colors = ['#d40505', '#b9840d', 'black', 'green', 'blue']

ft = tf.Font(family='微软雅黑', size=10)  # 有很多参数
for idx, color in enumerate(colorNames):
    inputText.tag_add(color, END)  # 申明一个tag,在a位置使用
    # 设置tag即插入文字的大小,颜色等
    inputText.tag_config(color, foreground=colors[idx], font=ft)

texts = []

textsOldLength = 0


def loopText():
    global textsOldLength
    length = len(texts)
    while len(texts) > 100:
        texts.pop(0)

    if textsOldLength < length:
        for text in texts:
            color = text.get('color')
            txt = text.get('text')
            if color in colorNames:
                inputText.insert(END, f'\n\n{txt}', color)
            else:
                inputText.insert(END, f'\n\n{txt}')
        inputText.see(END)

    textsOldLength = len(texts)

    inputText.after(30, loopText)


loopText()


def setStatusText(text, color='default'):
    texts.append({
        'text': text,
        'color': color
    })


# 读取配置

configPath = 'config/config.json'


def readConfig():
    with open(configPath, 'r', encoding='utf-8') as f:
        data = json.loads(f.read() or '{}')
        f.close
    return data


def writeConfig():
    config['downloadPath'] = downloadPath.get()
    with open(configPath, 'w') as f:
        f.write(json.dumps(config))
        f.close


if not os.path.exists(configPath):
    config = {
        'sessData': '',
        'downloadPath': 'download',
        'isClip': '0'
    }
    with open(configPath, 'w') as f:
        f.write(json.dumps(config))
        f.close


config = readConfig()
sessData = config.get('sessData') or ''
downloadPath.set((config.get('downloadPath') or 'download').replace(
    '/', sep).replace('\\', sep))
isClip = config.get('isClip') or '0'
if isClip == '1':
    clipButton.select()


def filterName(name):
    regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$)')
    space = re.compile(r'\s{2,}')
    return space.sub(" ", regexp.sub("", name))


clipData = ''
clipUrls = []


def writeClip(data):
    with open('config/clipsgui.txt', 'w') as f:
        f.write('\n'.join(data))
        f.close


def readClip():
    data = ''
    if os.path.exists('config/clipsgui.txt'):
        with open('config/clipsgui.txt', 'r', encoding='utf-8') as f:
            data = f.read() or ''
            f.close

    return readUrls(data)


def appendClip(url):

    if url in clipUrls:
        return False

    clipUrls.append(url)
    writeClip(clipUrls)


clipUrls = readClip()

if clipUrls:
    for i in clipUrls:
        appendWaiting(i)


def removeClip(url):
    try:
        clipUrls.remove(url)
        writeClip(clipUrls)
    except BaseException:
        pass


def listenerClip():
    '''
        读取剪贴板
    '''
    global clipData

    while 1:
        if clupValue.get() == 1:

            jiantieban = pyperclip.paste() or ''
            if jiantieban != clipData:
                clipData = jiantieban
                urls = readUrls(clipData)
                if urls:
                    for url in urls:
                        if url in clipCaches:
                            continue
                        clipCaches.append(url)
                        appendWaiting(url)
                        setStatusText(f'\n\n收到剪贴板的url:{url}\n')

        time.sleep(0.1)


def callbackFunc(data):
    _type = data.get('type')
    if _type == 'progress':
        index = data.get('index')
        total = data.get('total')
        name = data.get('name')
        title = data.get('title')
        for item in progress:
            if item['name'] == name:
                if index:
                    item['index'] = index
                if total:
                    item['total'] = total
                if title:
                    item['title'] = title
                if index >= total and item['item_index'] >= item['item_total']:
                    item['done'] = True
                break
    if _type == 'data':
        name = data.get('name')
        for item in progress:
            if item['name'] == name:
                index = data.get('index')
                total = data.get('total')
                title = data.get('title')
                if title:
                    item['title'] = title

                if index:
                    item['item_index'] = index
                if total:
                    item['item_total'] = total
                if index >= total and item['index'] >= item['total']:
                    item['done'] = True
                    break
    if _type == 'msg':
        msg = data.get('msg')
        color = data.get('color')
        if msg:
            setStatusText(msg, color=color)


def get(func, url=None):
    if url is None:
        return {"msg": "请输入链接"}
    f = None
    for key in funcMap:
        if(key in url):

            path = f'{downloadPath.get()}\\{key}'

            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except BaseException:
                    pass

            if key == 'bilibili':
                data = bilibili.get(url, savepath=path,
                                    func=func, sessData=sessData)
                return {}
            if key == 'mgtv':
                data = mgtv.get(url, savepath=path,
                                func=func)
                return {}
            if key == 'iqiyi':
                data = iqiyi.get(url, savepath=path,
                                 func=func)
                return {}
            if key == 'v.qq':
                data = qqtv.get(url, savepath=path,
                                func=func)
                return {}
            if key == 'douyin':
                data = douyin.get(url, func=func)
                data['pathname'] = path
                return data
            else:
                f = funcMap[key]
                data = f.get(url)
                data['pathname'] = path
                return data

    return {"msg": "链接无法解析"}


def spider(func, url):
    data = get(func, url)

    text = data.get("text")
    msg = data.get("msg")
    if msg or text:
        setStatusText(f'{text}:{msg or text}')
        func({
            'type': 'data',
            'name': url,
            'index': 1,
            'total': 1
        })
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

    index = 0
    length = len(imgs or []) + len(audios or []) + len(videos or [])
    if length == 0:
        func({
            'type': 'data',
            'name': url,
            'index': 1,
            'total': 1
        })
        func({
            'type': 'progress',
            'name': url,
            'index': 1,
            'total': 1
        })
        return

    func({
        'type': 'data',
        'name': url,
        'title': file_name,
        'index': index,
        'total': length
    })
    for v in downs:
        for vv in v['data']:
            _url = vv
            _headers = None
            if not isinstance(vv, str):
                if vv['name']:
                    file_name = filterName(vv['name'])
                _url = vv['url']
                _headers = vv.get('headers', None)

            func({
                'type': 'data',
                'name': url,
                'title': file_name,
                'index': index,
                'total': length
            })
            download(_url, file_name=file_name,
                     file_type=v['type'], save_path=savePath, headers=_headers, func=func, pname=url)
            index += 1
            func({
                'type': 'data',
                'name': url,
                'index': index,
                'total': length
            })


def start(url):
    appendProgress(url)


def loopList():
    while 1:

        length = len(progress)-1
        while length >= 0:
            if progress[length]['done'] == True:
                setStatusText(
                    f'{progress[length]["title"]}:{progress[length]["name"]} 下载完成!', color='success')
                removeClip(progress[length]['name'])
                progress.pop(length)
            length -= 1

        while len(progress) < 5 and len(waiting) > 0:
            if not os.path.exists(downloadPath.get()):
                try:
                    os.path.makedirs(downloadPath.get())
                except BaseException:
                    setStatusText(f'{downloadPath.get()} 路径不存在')
                break
            url = waiting.pop(0)
            t = threading.Thread(
                target=start, args=(url,))
            t.setDaemon(True)
            t.start()

        time.sleep(1)


t1 = threading.Thread(target=loopList)
t1.setDaemon(True)
t1.start()

t2 = threading.Thread(target=listenerClip)
t2.setDaemon(True)
t2.start()


def closeWindow():
    ans = messagebox.askyesno(title='提示', message='是否确认关闭?')
    if ans:
        top.destroy()
    else:
        return


top.protocol('WM_DELETE_WINDOW', closeWindow)


top.mainloop()
