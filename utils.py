

import os
import re
from datetime import datetime
import click
import requests
import subprocess
import math


def filter_name(name):
    """
    过滤文件名
    """
    regexp = re.compile(r'(/|\\|:|\?|\*|\||"|\'|<|>|\$|\u2027)')
    space = re.compile(r'\s{2,}')
    return space.sub(" ", regexp.sub("", name))


def check_dir(path):
    """
    检查文件夹是否存在，存在返回True;不存在则创建，返回False
    """
    if not os.path.exists(path):
        os.makedirs(path)
        return False
    return True


def callbackMsg(func, msg, color=None):
    if func:
        func({
            'type': 'msg',
            'msg': msg,
            'color': color,
        })


def printMsg(func, msg, color=None):
    if func:
        callbackMsg(func, msg, color)
    else:
        print(msg)


def download(file_url, file_name=None, file_type=None, save_path="download", headers=None, func=None, pname=''):
    """
    :param file_url: 下载资源链接
    :param file_name: 保存文件名，默认为当前日期时间
    :param file_type: 文件类型(扩展名)，也是保存路径
    :param save_path: 保存路径，默认为download,后面不要"/"
    :param headers: http请求头，默认为iphone
    """
    if file_name is None:
        file_name = str(datetime.now())
    file_name = filter_name(file_name)

    if file_type is None:
        if "." in file_url:
            file_type = file_url.split(".")[-1]
        else:
            file_type = "uknown"

    check_dir(f"{save_path}")
    file_name = file_name + "." + file_type

    if headers is None:
        headers = {
            "User-Agent":
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1"
        }

    # 下载提示
    writeIndex = 0
    fullPath = f"{save_path}/{file_name}"
    with requests.get(file_url, headers=headers, stream=True) as rep:
        file_size = int(rep.headers['Content-Length'])
        if rep.status_code != 200:
            printMsg(func, "下载失败", color='err')
            return False

        if os.path.isfile(fullPath):
            fsize = os.path.getsize(fullPath)
            if abs(fsize-file_size) < 500:
                printMsg(func, fullPath+"文件已存在", color='err')
                return True

        label = '{:.2f}MB'.format(file_size / (1024 * 1024))
        if func:
            with open(fullPath, "wb") as f:
                for chunk in rep.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        writeIndex += 1024
                        func({
                            'name': pname,
                            'type': 'progress',
                            'index': writeIndex,
                            'total': file_size
                        })
        else:
            with click.progressbar(length=file_size, label=label) as progressbar:
                with open(fullPath, "wb") as f:
                    for chunk in rep.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            progressbar.update(1024)

        if os.path.exists(fullPath) and file_type == 'mp4':
            printMsg(func, f"{file_name} 开始生成封面", color='success')
            arr = fullPath.split('.')
            arr[-1] = 'jpg'
            imgPath = '.'.join(arr)
            child = subprocess.Popen(
                f'ffmpeg -loglevel error -i "{fullPath}" -f image2 -frames:v 1 "{imgPath}" -y', shell=True)
            child.wait()
            printMsg(func, f"{file_name} 生成封面成功", color='success')

        printMsg(func, "下载成功", color='success')
        return True
