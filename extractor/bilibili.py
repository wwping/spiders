

import re
from extractor import bilibili2
from extractor import bilibili3


def get(url: str, savepath: str = 'download', func=None, sessData: str = '') -> dict:
    bv = re.findall(r'video/(BV[0-9a-zA-Z]*)', url)
    if bv:
        return bilibili2.get(url, savepath, func=func, sessData=sessData)
    else:
        return bilibili3.get(url, savepath, func=func, sessData=sessData)


if __name__ == "__main__":
    print(get(input("url: ")))
