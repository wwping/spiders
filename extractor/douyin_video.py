import re

import requests

class DouyinVideo:
    def __init__(self,url, func=None):
        self.name = url
        self.func = func
        self.url = url

        self.total = 1
        self.index = 0

    def callback(self, title=None):
        if self.func:
            self.func({
                'type': 'data',
                'name': self.name,
                'total': self.total,
                'index': self.index,
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

    def done(self,msg):
        self.total = 1
        self.index = 1
        self.callback(msg)

    def run(self) -> dict:
        """
        author, title, audioName, audios, videoName, videos
        """

        self.callback('拉取数据')

        data = {}
        headers = {
            'accept': 'application/json',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        api = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={item_id}&dytk={dytk}"

        # get html text
        rep = requests.get(self.url, headers=headers, timeout=10)
        if not rep.ok:
            self.printMsg("获取失败",color="err")
            return data

        html_text = rep.text

        # get item_id, dytk
        item_id = re.findall(r'itemId: "(\d+)"', html_text)
        dytk = re.findall(r'dytk: "(.*?)"', html_text)
        if not item_id or not dytk:
            self.printMsg("获取失败",color="err")
            return data
        item_id = item_id[0]
        dytk = dytk[0]

        # get video info
        rep = requests.get(api.format(item_id=item_id, dytk=dytk), headers=headers, timeout=6)
        if not rep.ok or not rep.json()["status_code"] == 0:
            self.printMsg("获取失败",color="err")
            return data
        info = rep.json()["item_list"][0]

        data["author"] = info["author"]["nickname"]
        data["title"] = data["videoName"] = info["desc"]
        data["audioName"] = data["title"]
        data["audios"] = [info["music"]["play_url"]["uri"]]
        # data["imgs"] = [info["video"]["origin_cover"]["url_list"][0]]

        # get playwm_url -> play_url
        play_url = info["video"]["play_addr"]["url_list"][0].replace('playwm', 'play')

        rep = requests.get(play_url, headers=headers, allow_redirects=False, timeout=6)
        video_url = rep.headers.get('location', '')
        data["videos"] = [video_url]

        return data

def get(url: str,  func=None) -> dict:
    douyin =  DouyinVideo(url,func)

    return douyin.run()
