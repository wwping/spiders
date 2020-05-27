
from .music163 import Wangyiyun


def get(url: str) -> dict:
    """
    aduios或者videos
    """
    data = {}
    wangyiyun = Wangyiyun()
    resource_url = wangyiyun.get(url)
    if not resource_url:
        return {"msg": "获取失败"}
    if "mv" in url or "video" in url:
        data["videos"] = [{
            'url': resource_url.get('url'),
            'name': resource_url.get('name'),
        }]
    elif "song" in url:
        data["audios"] = [{
            'url': resource_url.get('url'),
            'name': resource_url.get('name'),
        }]
    return data


__all__ = ["get"]
