

# @wwping
import re

import requests


def get(url: str) -> dict:
    """
    title、imgs、videos
    """
    data = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
        "Cookie": "didv=1588309328000; did=web_4042d9ccec7a484d97ed6abd43d5f2fd; sid=5bb2e5c80ac84c5d6744dac8",
        "Referer": url,
    }
    re_title = r'<meta name="description" itemprop="description" content="(.*?)">'
    re_video = r';srcNoMark&#34;:&#34;(https://.*?\.mp4)'
    re_img = r'&#34;path&#34;:&#34;(.*?\.jpg)&#34;'

    rep = requests.get(url, headers=headers, timeout=10)
    if rep.status_code != 200:
        return {"msg": f"{rep.status_code}获取失败"}

    title = re.findall(re_title, rep.text)
    video = re.findall(re_video, rep.text)
    img = re.findall(re_img, rep.text)
    if title:
        data["title"] = title[0]
    if video:
        data["videos"] = video
# https://js2.a.yximgs.com/ufile/atlas/NTE5Njg3MjUyMDE5MTk4MTM4OF8xNTg0NzkyNzI4MjAy_15.jpg
    if img:
        data["imgs"] = ["https://js2.a.yximgs.com" +
                        i for i in img[:-1]]  # 最后一张是水印
    return data


if __name__ == "__main__":
    print(get(input("url: ")))
