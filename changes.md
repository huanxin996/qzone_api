# 更新说明

## 1.1.0

补齐说说编辑、评论管理、留言板、访客、日志

### 说说相关补充

- `edit_message`：编辑已发的说说（`emotion_cgi_update`），可以同时改可见范围。注意这个接口的 `g_tk` 要用 `p_skey` 算
- `like_comment`：给说说下的某条评论点赞（走 `internal_dolike_app`，`unikey` 指向 `{主人QQ}_{说说tid}_{评论id}`）
- `delete_comment`：删除说说下的评论（`emotion_cgi_delcomment_ugc`）
- `delete_reply`：删除评论下的回复（`emotion_cgi_delreply_ugc`）
- 发说说 / 编辑说说支持选私密模式：`publish_message` / `edit_message` 新增 `ugc_right` 参数，取值 `1` 所有人 / `4` QQ好友 / `16` 部分好友可见 / `64` 仅自己可见 / `128` 部分好友不可见，也可以直接用导出的常量 `UGC_RIGHT_ALL` / `UGC_RIGHT_FRIEND` / `UGC_RIGHT_PART` / `UGC_RIGHT_SELF` / `UGC_RIGHT_EXCLUDE`
- 在说说里 @某人：用 `format_mention(qq号, 昵称)` 生成 `@{uin:QQ,nick:昵称,who:1}`
- `指定某人可见 / 指定某人不可见`：两种模式用的是同一个字段 `allow_uins`（准[]列表），区别只在 `ugc_right`——`16` 表示名单里的人可见、`128` 表示名单里的人不可见`publish_message` / `edit_message` 新增 `uins` 参数（QQ 号列表），只在 `ugc_right=16/128` 时生效，底层自动拼成 `allow_uins`, 发布响应的 HTML 里能看到对应的 `data-accessright="16"` / `data-accessright="128"`
- 在说说里 @某人：用 `format_mention(qq号, 昵称)` 生成 `@{uin:QQ,nick:昵称,who:1}` 
- `delete_message`：抓包确认官方删除走 `emotion_cgi_delete_v6`，`topicId` 形如 `{uin}_{feedsKey}__1`。现在只要传说说列表里的 `cur_key`（feedsKey）即可
  
### 留言板

- `get_message_board`：留言板留言列表，返回每条留言的 id、留言者、内容、时间、是否私密、回复数
- `post_message_board`：在某人留言板发留言
- `delete_message_board`：删留言（`del_msgb`），要传留言 id 和该留言留言者的 QQ。参数用 `idList`/`uinList`，走 h5 域名

### 访客

- `get_visitors`：自己空间的访客列表（`cgi_get_visitor_simple`），返回访客 QQ、昵称、来访时间、是否好友、头像，以及累计访问量。只能查自己的访客

### 日志

- `list_blogs`：日志列表，每条带 `blogId`（编辑 / 删除时用）、标题、时间、评论数、分类
- `publish_blog`：发日志，`content` 传正文 HTML，`right_type` 控制可见范围（`1` 公开 / `2` QQ好友 / `3` 指定 / `4` 仅自己）
- `edit_blog`：编辑已发日志（`mod_blog`），`blog_id` 取自 `list_blogs`。
- `delete_blog`：删日志（`del_blog`）

### 其它

- 顶层导出 `format_mention` 和 `UGC_RIGHT_*` 常量，`from qzone_api import format_mention, UGC_RIGHT_SELF` 直接可用
- 留言内容解析改用服务端的 `htmlContent` 字段（之前取 `content` 拿到的是空串）

> 留言板、访客、日志这几组接口的 `g_tk` 都用 `p_skey` 算；`edit_message` 也一样。

## 1.0.0

补齐图片相关的接口，统一了方法命名，同时保留了旧方法名

### 新增的接口

- `upload_image`：上传一张图片到空间相册，拿到图片信息（`data`）后用于发说说或评论
- `publish_image_message`：发纯图片说说或图文说说（`content` 传空就是纯图片，传文字就是图文）
- `comment_message_with_images`：发评论，可以只发文字，也可以带图
- `reply_comment`：回复别人（或自己）的评论，同样支持带图
- `list_albums`：拉相册列表（自己的，或对方公开可见的），返回相册 id、名称、封面、照片数、权限等
- `list_album_photos`：拉某个相册里的图片列表，返回每张图的 `lloc`/`sloc`、url、尺寸、上传时间等
- `delete_photo`：删自己相册里的某张图片（只能删当前登录账号名下的），走 `cgi_delpic_multi_v2`


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

### 数据获取的变化

- `get_messages_list` 和 `get_friend_feeds` 现在多了 `begintime` 参数，传一个时间戳就只拉这个时间点之前的内容，方便往前翻页
- 解析说说时多带了几项数据：评论列表、点赞列表、评论总数、来源设备、视频信息、转发的原文
- 评论列表里每条评论带上了评论 id（服务端的 `tid` 字段，回复评论时直接传给 `comment_id`）、评论里的图片、回复数和回复列表

### 修的问题

- 请求返回值统一了：能解析成 JSON 就返回 dict，解析不了就返回原始文本，请求本身失败（网络错误、状态码不对）返回 `None`，不会再出现"失败了却当成功"的情况
- 服务端偶尔返回 `msglist` / `commentlist` / `pic` / `video` 为空（null）时，解析不会再直接崩掉
- 修了 HTML 解析函数的拼写（`html_unescape`），旧的 `html_unesape` 拼写留作别名
- 清掉了之前重复的 import、重复的方法定义、写了一半的字典和取不到的返回值

### 依赖

- `aiohttp>=3.12.0`
- `requests>=2.32.4`
- 其余：`lxml`、`loguru`、`pyzbar`、`Pillow`、`qrcode`

### 要注意的一点

下面这些接口用的 `g_tk` 要用 `p_skey` 算，不是登录默认给的那个 `bkn`：上传图片（`upload_image`）、图文评论（`comment_message_with_images`）、回复评论（`reply_comment`）、编辑说说（`edit_message`）、留言板（`get_message_board` / `post_message_board` / `delete_message_board`）、访客（`get_visitors`）、日志（`list_blogs` / `publish_blog` / `edit_blog` / `delete_blog`）、相册（`list_albums` / `list_album_photos` / `delete_photo`）。也就是：

```python
from qzone_api.utils import bkn
g_tk_pskey = bkn(cookies["p_skey"])
```

其余接口用登录返回的 `bkn`（由 `skey` 算出）就行
