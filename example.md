<!-- markdownlint-disable MD024 MD036 MD041 -->
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

> 私密/加密相册的访问控制在腾讯服务端，没有绕过的接口，这个库不提供越权查看他人隐私相册的功能。

## 编辑说说 / 私密模式 / @某人

`edit_message` 用的 `g_tk` 要用 `p_skey` 算（`g_tk_pskey`），可见范围用 `ugc_right`：

```python
from qzone_api import UGC_RIGHT_SELF, format_mention

# 发一条只有自己可见、并且 @了某人的说说
content = "测试 " + format_mention(10001, "张三")   # -> "测试 @{uin:10001,nick:张三,who:1}"
resp = await qzone.publish_message(qq, content, cookies_str, g_tk, ugc_right=UGC_RIGHT_SELF)
tid = resp["tid"]

# 编辑刚发的说说，改成所有人可见
await qzone.edit_message(qq, tid, "改过的内容", cookies_str, g_tk_pskey, ugc_right=1)
```

## 指定某人可见 / 指定某人不可见

可见范围取值（`from qzone_api import UGC_RIGHT_*`）：

| 常量 | 值 | 含义 |
| --- | --- | --- |
| `UGC_RIGHT_ALL` | 1 | 所有人可见 |
| `UGC_RIGHT_FRIEND` | 4 | 好友可见 |
| `UGC_RIGHT_PART` | 16 | **指定名单里的人可见**（其他人看不到） |
| `UGC_RIGHT_SELF` | 64 | 仅自己可见 |
| `UGC_RIGHT_EXCLUDE` | 128 | **指定名单里的人不可见**（其他人能看到） |

`ugc_right=16` 和 `ugc_right=128` 都要配合 `uins`（QQ 号列表）使用，
底层拼成官方的 `allow_uins`（逗号分隔）字段——两者字段名相同，只是语义相反：

```python
from qzone_api import UGC_RIGHT_PART, UGC_RIGHT_EXCLUDE
 
# 只给 10001、10002 两个人看
await qzone.publish_message(qq, "只给你们看", cookies_str, g_tk,
                            ugc_right=UGC_RIGHT_PART, uins=[10001, 10002])
 
# 除了 10001 别人都能看（对 10001 屏蔽）
await qzone.publish_message(qq, "就不给某人看", cookies_str, g_tk,
                            ugc_right=UGC_RIGHT_EXCLUDE, uins=[10001])
 
# 编辑说说时同样可以改名单（g_tk 用 p_skey 版）
await qzone.edit_message(qq, tid, "改一下名单", cookies_str, g_tk_pskey,
                         ugc_right=UGC_RIGHT_PART, uins=[10001, 10003])
```

> `uins` 只在 `ugc_right=16/128` 时生效，其它取值会被忽略。

## 删除说说

`delete_message` 只需要说说列表里该条的 `cur_key`（feedsKey）和 `timestamp`，
内部会自动拼成官方要求的 `topicId`（`{uin}_{feedsKey}__1`）：

```python
ms = await qzone.get_messages_list(qq, g_tk, cookies_str)
feed = ms["data"][0]
await qzone.delete_message(qq, feed["cur_key"], cookies_str, g_tk,
                           feed["cur_key"], feed["timestamp"])
```

## 评论：点赞 / 删除评论 / 删除回复

评论 id 从 `get_messages_list` 解析出的每条评论的 `id` 拿：

```python
ms = await qzone.get_messages_list(qq, g_tk, cookies_str)
feed = ms["data"][0]
tid = feed["tid"]
cmt = feed["comments"][0]
comment_id = cmt["id"]

# 给这条评论点赞
await qzone.like_comment(qq, qq, tid, comment_id, cookies_str, g_tk)

# 删除评论下的某条回复
reply_id = cmt["replies"][0]["id"]
await qzone.delete_reply(qq, qq, tid, comment_id, reply_id, cookies_str, g_tk)

# 删除评论本身
await qzone.delete_comment(qq, qq, tid, comment_id, cookies_str, g_tk)
```

## 留言板

`g_tk` 用 `p_skey` 算：

```python
# 读留言
mb = await qzone.get_message_board(host_qq, qq, g_tk_pskey, cookies_str, start=0, num=10)
for m in mb["messages"]:
    print(m["id"], m["name"], m["content"])

# 发留言
await qzone.post_message_board(host_qq, qq, "来逛逛", cookies_str, g_tk_pskey)

# 删留言（要传留言 id 和该留言留言者的 QQ）
first = mb["messages"][0]
await qzone.delete_message_board(host_qq, first["id"], first["uin"], cookies_str, g_tk_pskey)
```

## 访客

只能查自己的访客，`g_tk` 用 `p_skey` 算：

```python
vs = await qzone.get_visitors(qq, g_tk_pskey, cookies_str, page=1, count=20)
print("累计访问量:", vs["total_visit"])
for v in vs["visitors"]:
    print(v["uin"], v["name"], v["time"], v["is_friend"])
```

## 日志

`g_tk` 用 `p_skey` 算：

```python
# 列表
bl = await qzone.list_blogs(qq, qq, g_tk_pskey, cookies_str, pos=0, num=15)
for b in bl["blogs"]:
    print(b["id"], b["title"], b["time"])

# 发日志（正文是 HTML；right_type: 1公开 2好友 3指定 4仅自己）
resp = await qzone.publish_blog(qq, "标题", "<p>正文</p>", cookies_str, g_tk_pskey, right_type=1)

# 编辑
blog_id = bl["blogs"][0]["id"]
await qzone.edit_blog(qq, blog_id, "新标题", "<p>新正文</p>", cookies_str, g_tk_pskey)

# 删除
await qzone.delete_blog(qq, qq, blog_id, cookies_str, g_tk_pskey)
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
