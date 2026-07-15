# 更新说明

## 1.0.0

补齐了图片相关的接口，统一了方法命名，同时保留了旧方法名。

### 新增的接口

- `upload_image`：上传一张图片到空间相册，拿到图片信息（`data`）后用于发说说或评论。
- `publish_image_message`：发纯图片说说或图文说说（`content` 传空就是纯图片，传文字就是图文）。
- `comment_message_with_images`：发评论，可以只发文字，也可以带图。
- `reply_comment`：回复别人（或自己）的评论，同样支持带图。
- `list_albums`：拉相册列表（自己的，或对方公开可见的），返回相册 id、名称、封面、照片数、权限等。
- `list_album_photos`：拉某个相册里的图片列表，返回每张图的 `lloc`/`sloc`、url、尺寸、上传时间等。
- `delete_photo`：删自己相册里的某张图片（只能删当前登录账号名下的），走 `cgi_delpic_multi_v2`。

> 相册接口只覆盖账号自身权限范围内的内容：自己的相册，以及对方设为公开的相册。私密/加密相册由腾讯服务端做访问控制，没有可绕过的接口，也没有实现这类功能。

### 命名调整

参数构建函数统一改成了 `build_` 开头，返回值就是可以直接丢给请求的 dict：

| 现在的名字 | 旧名字（还能用） |
| --- | --- |
| `build_like_params` | `like_feed` |
| `build_friend_feeds_params` | `get_feeds` |
| `build_messages_params` | `get_self_zone` |
| `build_publish_params` | `get_send_zone` |
| `build_comment_params` | `get_send_comment` |
| `build_delete_params` | `get_del_zone` |
| `build_forward_params` | `get_forward_zone` |

API 方法也一样，旧名字作为别名保留：

| 现在的名字 | 旧名字（还能用） |
| --- | --- |
| `get_messages_list` / `fetch_messages_raw` | `_get_messages_list` |
| `get_friend_feeds` / `fetch_friend_feeds_raw` | `_get_zone` |
| `like_feed` | `_zanzone` |
| `publish_message` | `_send_zone` |
| `comment_message` | `_send_comments` |
| `forward_message` | `_forward_zone` |
| `delete_message` | `_del_zone` |

也就是说，`_send_zone` 这类老写法调用的还是同一个函数，行为没变。

### 数据获取的变化

- `get_messages_list` 和 `get_friend_feeds` 现在多了 `begintime` 参数，传一个时间戳就只拉这个时间点之前的内容，方便往前翻页。
- 解析说说时多带了几项数据：评论列表、点赞列表、评论总数、来源设备、视频信息、转发的原文。
- 评论列表里每条评论带上了评论 id（服务端的 `tid` 字段，回复评论时直接传给 `comment_id`）、评论里的图片、回复数和回复列表。

### 修的问题

- 请求返回值统一了：能解析成 JSON 就返回 dict，解析不了就返回原始文本，请求本身失败（网络错误、状态码不对）返回 `None`，不会再出现"失败了却当成功"的情况。
- 服务端偶尔返回 `msglist` / `commentlist` / `pic` / `video` 为空（null）时，解析不会再直接崩掉。
- 修了 HTML 解析函数的拼写（`html_unescape`），旧的 `html_unesape` 拼写留作别名。
- 清掉了之前重复的 import、重复的方法定义、写了一半的字典和取不到的返回值。

### 依赖

- `aiohttp>=3.12.0`
- `requests>=2.32.4`
- 其余：`lxml`、`loguru`、`pyzbar`、`Pillow`、`qrcode`

### 要注意的一点

上传图片（`upload_image`）、图文评论（`comment_message_with_images`）、回复评论（`reply_comment`）这三个接口用的 `g_tk` 要用 `p_skey` 算，不是登录默认给的那个 `bkn`。也就是：

```python
from qzone_api.utils import bkn
g_tk_pskey = bkn(cookies["p_skey"])
```

其余接口用登录返回的 `bkn`（由 `skey` 算出）就行。
