# xinger-api

这里实际上包含了我很多个想法...包括GitHub repo、seewo、local、CDN做图源...

最终选择seewo，其他脚本基本上是废稿，如果有别的想法欢迎提 issue

通过 `pip install -r requirements.txt` 安装前置库，不确定是否有用到2333，`fastapi` 和 `uvicorn` 是必须的

运行 `seewo.py` 并配置 `seewo_config.json` 以上传本地图片到希沃图床，需要先在浏览器获取 cookie，图片信息会缓存到 `seewo_cache.json`

运行 `main.py` 以启动服务端...请在 `config.json` 配置一些必要参数

总而言之如果有人要用的话我会重构一份的...本意只是给 [Xinger](https://xinger.vip) 做背景图片的而已，一次性脚本

> **Warning**  
> 已知图片直接返回 Fastapi 的 RedirectResponse 导致浏览器直接访问 api 时会直接下载  
> 虽然不算 bug ，但不爽...尚无思路解决此问题...  
> 可能是 Content-type 之类的导致的？i don't know...
