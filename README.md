
### 环境依赖

- 需要python环境
- 某些视频下载需要 java环境 
- 需要用到 selenium webdriver ,请将 chromedriver.exe 赋值到python安装根目录 , 如果不兼容请自行下载兼容版本
- 下载地址 http://chromedriver.storage.googleapis.com/index.html
- 需要用到  browsermob-proxy
- 下载地址  https://github.com/lightbody/browsermob-proxy/releases

### 配置文件
```bash
{
    "downloadPath": "download", // 默认的下载路径 如果没配置具体的下载路径或者 具体的下载路径无法创建
    "isInput": "1", //命令行模式下  0自动读取剪贴板  1手动输入
    "isClip": "0", //UI模式下  是否自动读取剪贴板  1开启
}
```


### 支持哪些
- 抖音视频分享链接，下载单个视频    https://v.douyin.com/w3G93b/
- 抖音用户分享连接，下载用户所有视频

- bilibili视频，下载所有P   https://www.bilibili.com/video/BV1mp4y1X7sr
- bilibili番剧，下载所有P   

- acfun视频链接  https://www.acfun.cn/v/ac15179107
- 5sing音乐链接 http://5sing.kugou.com/fc/17457264.html
- 酷狗音乐链接 https://www.kugou.com/song/#hash=86B0B6CCBE1341065931558886E4C07F&album_id=37236081
- 酷我音乐链接 http://www.kuwo.cn/play_detail/1850233
- 酷6视频  https://www.lizhi.fm/1244717/2587320075826653702
- 好看视频 https://haokan.baidu.com/v?vid=10046831123777078980&tab=recommend
- 网易云音乐 https://music.163.com/#/song?id=5266159
- QQ音乐 分享链接 https://c.y.qq.com/base/fcgi-bin/u?__=eawrb35
- 芒果tv https://www.mgtv.com/b/337284/8174348.html?cxid=95kqkw8n6
- 爱奇艺视频 https://www.iqiyi.com/v_19ry8g1ngc.html
- 腾讯视频 https://v.qq.com/x/cover/r5trbf8xs5uwok1.html
- 乐视tv http://www.le.com/ptv/vplay/1964428.html


### 怎么运行
```bash
//界面
python gui.py  或者运行 start.bat
//windows 不打开黑窗口直接运行, 使用 browsermob-proxy 的时候创建代理，总会弹出一个黑乎乎的窗口
gui.pyw
```

![image](https://github.com/wwping/spiders/blob/master/1.png?raw=true)


### 记录缓存
UI模式下 在 clipsgui.txt 可以保存你的 等待连接url  最好每行一个，当程序启动的时候回去拿这个来下载

### 单独未集成的几个
| 文件 | 说明   |
| ---------- | --------- |
| testimage.py   | 片片     |
| zzzttt.py   | 片片     |
| pcav.py  | 省市区数据     |


### 如果侵权，请联系我们，我们将会删除代码  1069410172@qq.com

### 仅用于代码交流，请勿用于违法犯罪活动

