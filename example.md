# 使用示例

下面按实际使用流程走一遍：登录、拿列表、发说说、发图、评论、回复、点赞、转发、删除。所有方法都是异步的，需要在 `async` 函数里 `await` 调用。

## 登录，准备参数

```python
import asyncio
from qzone_api import QzoneApi, QzoneLogin
from qzone_api.utils import bkn

async def main():
    login = QzoneLogin()
    result = await login.login()   # 会生成二维码图片，用手机QQ扫码
    if result["code"] != 0:
        print("登录失败:", result["msg"])
        return

    qq = int(result["qq"].lstrip("o"))          # uin 形如 o12345678，去掉前缀
    cookies = result["cookies"]                 # dict
    cookies_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
    g_tk = result["bkn"]                        # 由 skey 算出，大部分接口用这个
    g_tk_pskey = bkn(cookies["p_skey"])         # 由 p_skey 算出，上传图片/图文评论/回复评论用这个

    qzone = QzoneApi()
    # 后面的示例都接在这里

asyncio.run(main())
```

库不会保存 cookies，需要自己管理。`skey` 和 `p_skey` 都在 `cookies` 里。

## 获取说说列表

```python
messages = await qzone.get_messages_list(
    target_qq=qq,        # 看谁的说说就填谁的QQ
    g_tk=g_tk,
    cookies=cookies_str,
    pos=0,               # 起始位置
    num=20,              # 拉多少条
)
```

返回结构：

```python
{
    "status": "ok",
    "total": 2,
    "data": [
        {
            "cur_key": "8a1b2c3d...",     # 说说的 tid，点赞/评论/删除都要用它
            "uin": 12345678,
            "timestamp": 1752570000,
            "content": "说说文字",
            "images": [{"url": "...", "width": 1080, "height": 720}],
            "videos": [],
            "repost": None,               # 转发的说说这里是原文信息
            "source": "iPhone",           # 来源设备
            "comment_count": 3,
            "comments": [
                {
                    "id": 2,                  # 评论ID，回复评论时传给 comment_id
                    "uin": ...,
                    "name": "...",
                    "content": "...",
                    "time": "...",
                    "timestamp": 1752570100,
                    "images": [{"url": "..."}],   # 评论里带的图
                    "reply_count": 1,
                    "replies": [{"id": 3, "uin": ..., "name": "...", "content": "...", "time": "...", "timestamp": ...}],
                },
            ],
            "likes": [{"uin": ..., "name": "..."}],
        },
    ],
}
```

往前翻旧说说，用 `begintime` 传一个时间戳，只拉这个时间点之前的：

```python
older = await qzone.get_messages_list(
    target_qq=qq, g_tk=g_tk, cookies=cookies_str,
    begintime=messages["data"][-1]["timestamp"],
)
```

需要原始响应文本的话用 `fetch_messages_raw`（参数一样），自己解析。

## 获取好友动态

```python
feeds = await qzone.get_friend_feeds(
    target_qq=qq,        # 自己的QQ
    g_tk=g_tk,
    cookies=cookies_str,
    page=1,
    count=10,
)
```

返回 `{"status": "ok", "data": [...]}`，每条带 `id`（unikey）、`tid`、`uin`、`nickname`、`content`、`images` 等。同样支持 `begintime`。原始文本用 `fetch_friend_feeds_raw`。

## 发文本说说

```python
resp = await qzone.publish_message(
    target_qq=qq,
    content="今天天气不错",
    cookies=cookies_str,
    g_tk=g_tk,
)
# resp["code"] == 0 即成功，resp["tid"] 是新说说的 tid
```

## 上传图片

```python
upload = await qzone.upload_image(
    target_qq=qq,
    image="photo.jpg",        # 本地路径，也可以直接传 bytes
    skey=cookies["skey"],
    p_skey=cookies["p_skey"],
    cookies=cookies_str,
    g_tk=g_tk_pskey,          # 注意：这里用 p_skey 算的 g_tk
)
pic = upload["data"]          # 里面有 url / albumid / lloc / sloc / width / height
```

## 发图片说说、图文说说

`images` 传上一步 `upload["data"]` 组成的列表，可以多张：

```python
# 纯图片说说（不写文字）
await qzone.publish_image_message(
    target_qq=qq, images=[pic], cookies=cookies_str, g_tk=g_tk,
)

# 图文混合说说
await qzone.publish_image_message(
    target_qq=qq, images=[pic], cookies=cookies_str, g_tk=g_tk,
    content="配图说两句",
)
```

## 评论

普通文字评论（走老接口）：

```python
await qzone.comment_message(
    target_qq=qq,          # 说说主人的QQ
    uin=qq,                # 自己的QQ
    content="路过评论一下",
    cookies=cookies_str,
    g_tk=g_tk,
    fid=tid,               # 说说的 tid（列表里的 cur_key）
)
```

图文评论（也可以只发文字，`images` 不传就行）：

```python
comment = await qzone.comment_message_with_images(
    target_qq=qq,
    uin=qq,
    content="评论带张图",
    fid=tid,
    cookies=cookies_str,
    g_tk=g_tk_pskey,       # 注意：这里用 p_skey 算的 g_tk
    images=[pic],          # upload_image 返回的 data 列表
)
comment_id = comment["data"]["id"]   # 回复评论要用
```

评论 id 有两个来源：

1. 自己刚发的评论：接口返回的 `data["id"]`（如上）；
2. 别人（或历史）的评论：`get_messages_list` 返回的每条说说里 `comments[i]["id"]`。

```python
messages = await qzone.get_messages_list(target_qq=qq, g_tk=g_tk, cookies=cookies_str)
first = messages["data"][0]
for c in first["comments"]:
    print(c["id"], c["name"], c["content"])   # 拿到 id 就能回复
```

## 回复评论

```python
await qzone.reply_comment(
    target_qq=qq,
    uin=qq,
    content="回复你一下",
    fid=tid,
    comment_id=comment_id,   # 被回复评论的 id
    cookies=cookies_str,
    g_tk=g_tk_pskey,         # 注意：这里也用 p_skey 算的 g_tk
    images=[pic],            # 可选，带图回复
)
```

## 点赞

```python
await qzone.like_feed(
    target_qq=qq,                     # 自己的QQ
    g_tk=g_tk,
    fid=tid,
    cur_key=f"http://user.qzone.qq.com/{host_qq}/mood/{tid}",
    uni_key=f"http://user.qzone.qq.com/{host_qq}/mood/{tid}",
    cookies=cookies_str,
)
```

`host_qq` 是说说主人的QQ。好友动态里 `id` 字段就是现成的 unikey，可以直接用。

## 转发

```python
resp = await qzone.forward_message(
    target_qq=host_qq,     # 原说说主人的QQ
    opuin=qq,              # 自己的QQ
    tid=tid,               # 原说说的 tid
    content="转发说两句",
    cookies=cookies_str,
    g_tk=g_tk,
)
# resp["tid"] 是转发后新说说的 tid
```

## 删除说说

```python
await qzone.delete_message(
    target_qq=qq,
    fid=tid,
    cookies=cookies_str,
    g_tk=g_tk,
    curkey=tid,
    timestamp=timestamp,   # 说说的发表时间戳（列表里的 timestamp）
)
```

## 相册

相册接口的 `g_tk` 用 `p_skey` 算（和上传图片一致）：

```python
from qzone_api.utils import bkn
g_tk_pskey = bkn(cookies["p_skey"])
```

### 相册列表

```python
# host_qq 是相册主人的QQ，uin 是自己的QQ
albums = await qzone.list_albums(host_qq, qq, g_tk_pskey, cookies_str)
# albums["albums"] 里每个相册：id / name / desc / photo_count / cover / rights / is_locked ...
```

看自己的相册就把 `host_qq` 传自己的QQ；看对方的传对方QQ，只能看到对方设为公开的相册。

### 相册里的图片

```python
album_id = albums["albums"][0]["id"]
photos = await qzone.list_album_photos(host_qq, qq, album_id, g_tk_pskey, cookies_str)
# photos["photos"] 里每张图：lloc / sloc / name / url / width / height / uploadtime ...
```

### 删自己相册里的图片

只能删当前登录账号名下的图片。`lloc`/`sloc` 从上面的图片列表拿，`priv` 是相册的 `rights`：

```python
p = photos["photos"][0]
priv = albums["albums"][0]["rights"]
resp = await qzone.delete_photo(
    uin=qq,
    album_id=album_id,
    lloc=p["lloc"],
    sloc=p["sloc"],
    cookies=cookies_str,
    g_tk=g_tk_pskey,
    priv=priv,
)
# resp["code"] == 0 且 resp["data"]["succ"] 里有对应 id 即删除成功
```

## 返回值和出错处理

- 请求成功且能解析出 JSON 时返回 dict，一般 `code == 0`（或 `err.code == 0`）表示成功；
- 返回内容解析不了时给原始文本；
- 网络错误、HTTP 状态码异常、参数构建出错时返回 `None`，具体原因看 loguru 日志。

所以判断成功与否大致是：

```python
resp = await qzone.publish_message(...)
if isinstance(resp, dict) and resp.get("code") == 0:
    print("成功")
else:
    print("失败:", resp)
```

## 旧方法名

老代码里的 `_send_zone`、`_zanzone`、`_get_zone`、`_get_messages_list`、`_send_comments`、`_forward_zone`、`_del_zone` 都还在，是新方法的别名，参数与新方法一致，不需要改动。
