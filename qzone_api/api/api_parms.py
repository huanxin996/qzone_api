"""QQ空间各接口的请求参数构建函数。

命名规范：所有参数构建函数以 ``build_`` 开头，返回可直接用于请求的 dict。
旧函数名（like_feed/get_feeds/get_self_zone/get_send_zone/get_send_comment/
get_del_zone/get_forward_zone）作为兼容别名保留。
"""
import re
import time
from typing import Dict, Any, List, Optional, Sequence


def _format_uin_list(uins: Optional[Sequence[int]]) -> str:
    """把 QQ 列表拼成 allow_uins 需要的逗号分隔字符串。"""
    if not uins:
        return ""
    return ",".join(str(u) for u in uins)


def build_like_params(opuin: int, appid: int = 311, fid: Optional[str] = None,
                      cur_key: Optional[str] = None, uni_key: Optional[str] = None) -> Dict[str, Any]:
    """构建点赞动态的请求参数"""
    params = {
        'qzreferrer': f'https://user.qzone.qq.com/{opuin}',  # 来源页
        'opuin': opuin,               # 操作者QQ
        'unikey': uni_key,            # 动态唯一标识
        'curkey': cur_key,            # 要操作的动态对象
        'appid': appid,               # 应用ID(说说:311)
        'from': 1,                    # 来源
        'typeid': 0,                  # 类型ID
        'abstime': int(time.time()),  # 当前时间戳
        'fid': fid,                   # 动态ID
        'active': 0,                  # 活动ID
        'format': 'json',             # 返回格式
        'fupdate': 1,                 # 更新标记
    }
    return params


def build_friend_feeds_params(uin: int, g_tk: int, page: int = 1, count: int = 10,
                              begintime: int = 0) -> Dict[str, Any]:
    """构建获取好友动态列表的请求参数"""
    params = {
        "uin": uin,              # QQ号
        "scope": 0,              # 访问范围
        "view": 1,               # 查看权限
        "filter": "all",         # 全部动态
        "flag": 1,               # 标记
        "applist": "all",        # 所有应用
        "pagenum": page,         # 页码
        "count": count,          # 每页条数
        "aisortEndTime": 0,      # AI排序结束时间
        "aisortOffset": 0,       # AI排序偏移
        "aisortBeginTime": 0,    # AI排序开始时间
        "begintime": begintime,  # 开始时间
        "format": "json",        # 返回格式
        "g_tk": g_tk,            # 令牌
        "useutf8": 1,            # 使用UTF8编码
        "outputhtmlfeed": 1      # 输出HTML格式
    }
    return params


def build_messages_params(target_qq: int, g_tk: int, pos: int = 0, num: int = 20,
                          begintime: int = 0) -> Dict[str, Any]:
    """构建获取指定QQ说说列表的请求参数"""
    params = {
        "uin": target_qq,         # 目标QQ
        "ftype": 0,               # 全部说说
        "sort": 0,                # 最新在前
        "pos": pos,               # 起始位置
        "num": num,               # 获取条数
        "replynum": 100,          # 评论数
        "g_tk": g_tk,             # 访问令牌
        "callback": "_preloadCallback",
        "code_version": 1,
        "format": "jsonp",
        "need_private_comment": 1
    }
    if begintime:
        params["begintime"] = begintime  # 只获取该时间戳之前的说说
    return params


# 说说/日志权限（ugc_right / rightType）取值说明见 format_mention / build_publish_params
UGC_RIGHT_ALL = 1        # 所有人可见
UGC_RIGHT_FRIEND = 4     # QQ好友可见
UGC_RIGHT_PART = 16      # 部分好友可见
UGC_RIGHT_SELF = 64      # 仅自己可见
UGC_RIGHT_EXCLUDE = 128  # 部分好友不可见


def format_mention(uin: int, nick: str) -> str:
    """生成说说/评论正文里 @某人 的富文本标记。

    直接把返回值拼进 content 即可，例如 ``f"你好 {format_mention(123, '张三')}"``。
    服务端/渲染端按 ``@{uin:QQ,nick:昵称,who:1}`` 解析为可点击的 @ 提及。
    """
    return "@{uin:%s,nick:%s,who:1}" % (uin, nick)


def build_publish_params(target_qq: int, content: str,
                         ugc_right: int = UGC_RIGHT_ALL,
                         uins: Optional[Sequence[int]] = None) -> Dict[str, Any]:
    """构建发表文本说说的请求参数。

    ugc_right 为可见范围：1 所有人 / 4 QQ好友 / 16 部分好友可见 /
    64 仅自己可见 / 128 部分好友不可见。@某人可用 :func:`format_mention` 拼进 content。

    uins 为指定名单（仅 ugc_right=16/128 时有意义）：真实抓包确认发布/编辑都用
    ``allow_uins`` 这一个字段传逗号分隔的 QQ 列表，ugc_right=16 时该列表是“指定这些人
    可见”，ugc_right=128 时是“指定这些人不可见”，字段名相同、语义由 ugc_right 决定。
    """
    params = {
        "syn_tweet_verson": 1,   # 说说版本
        "paramstr": 1,           # 参数
        "pic_template": "",      # 图片模板
        "richtype": "",          # 富文本类型
        "richval": "",           # 富文本值
        "hostuin": target_qq,    # 操作QQ
        "who": 1,                # 说说类型
        "con": content,          # 说说内容
        "feedversion": 1,        # 说说版本
        "ver": 1,                # 版本
        "ugc_right": ugc_right,  # 可见范围
        "to_sign": 0,            # 签名
        "code_version": 1,
        "format": "fs",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}"
    }
    if ugc_right in (UGC_RIGHT_PART, UGC_RIGHT_EXCLUDE) and uins:
        params["allow_uins"] = _format_uin_list(uins)  # 指定可见/不可见名单
    return params


def build_edit_message_params(target_qq: int, tid: str, content: str,
                              ugc_right: int = UGC_RIGHT_ALL,
                              ugcright_id: str = "",
                              uins: Optional[Sequence[int]] = None) -> Dict[str, Any]:
    """构建编辑已发说说（emotion_cgi_update）的请求参数。

    tid 为说说 id；ugcright_id 取自说说列表里该条的 ``ugcright_id``（可留空）。
    uins 与 :func:`build_publish_params` 一致：ugc_right=16/128 时用 ``allow_uins``
    传逗号分隔的 QQ 名单（16 指定可见、128 指定不可见）。
    """
    params = {
        "syn_tweet_verson": 1,
        "tid": tid,              # 要编辑的说说 id
        "paramstr": 1,
        "pic_template": "",
        "richtype": "",
        "richval": "",
        "special_url": "",
        "subrichtype": "",
        "con": content,          # 新内容
        "feedversion": 1,
        "ver": 1,
        "ugc_right": ugc_right,
        "to_sign": 0,
        "ugcright_id": ugcright_id,
        "hostuin": target_qq,
        "code_version": 1,
        "format": "fs",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}",
    }
    if ugc_right in (UGC_RIGHT_PART, UGC_RIGHT_EXCLUDE) and uins:
        params["allow_uins"] = _format_uin_list(uins)  # 指定可见/不可见名单
    return params


def build_comment_params(opuin: int, uin: int, content: str, fid: str) -> Dict[str, Any]:
    """构建发表说说评论的请求参数

    fid 可传说说 tid（自动补全为接口要求的 ``{opuin}_{tid}__1`` 格式），
    也可直接传完整 topicId。
    """
    topic_id = fid if "_" in str(fid) else f"{opuin}_{fid}__1"
    params = {
        "uin": uin,              # 目标QQ
        "hostUin": opuin,        # 操作QQ
        "feedsType": 100,        # 说说类型
        "inCharset": "utf-8",    # 字符集
        "outCharset": "utf-8",   # 字符集
        "topicId": topic_id,     # 说说ID（{opuin}_{tid}__1）
        "plat": "qzone",         # 平台
        "source": "ic",          # 来源
        "platformid": 50,        # 平台id
        "format": "fs",          # 返回格式
        "ref": "feeds",          # 引用
        "content": content,      # 评论内容
        "qzreferrer": f"https://user.qzone.qq.com/{opuin}",
    }
    return params


def build_upload_image_params(target_qq: int, pic_base64: str, skey: str,
                              p_skey: str, g_tk: int) -> Dict[str, Any]:
    """构建上传图片（cgi_upload_image）的请求参数。

    pic_base64 为图片的 base64 编码字符串；skey/p_skey 取自登录 cookies。
    """
    upload_url = f"https://up.qzone.qq.com/cgi-bin/upload/cgi_upload_image?g_tk={g_tk}"
    params = {
        "filename": "filename",   # 占位文件名
        "zzpanelkey": "",
        "uploadtype": "1",        # 上传类型
        "albumtype": "7",         # 说说相册
        "exttype": "0",
        "skey": skey,             # 登录 skey
        "zzpaneluin": str(target_qq),
        "p_uin": str(target_qq),
        "uin": str(target_qq),    # 操作QQ
        "p_skey": p_skey,         # 登录 p_skey
        "output_type": "json",    # 返回 json
        "qzonetoken": "",
        "refer": "shuoshuo",      # 来源：说说
        "charset": "utf-8",
        "output_charset": "utf-8",
        "upload_hd": "1",
        "hd_width": "2048",
        "hd_height": "10000",
        "hd_quality": "96",
        "backUrls": ("http://upbak.photo.qzone.qq.com/cgi-bin/upload/cgi_upload_image,"
                     "http://119.147.64.75/cgi-bin/upload/cgi_upload_image"),
        "url": upload_url,
        "base64": "1",            # picfile 为 base64
        "picfile": pic_base64,    # 图片内容
    }
    return params


def build_image_richval(images: List[Dict[str, Any]]) -> Dict[str, str]:
    """由图片上传返回的 data 列表构建发表图片说说所需的 richval / pic_bo。

    每个 image 为 :meth:`upload_image` 返回结果里的 ``data`` 字段。
    """
    richvals = []
    pic_bos = []
    for d in images:
        richvals.append(
            ",{albumid},{lloc},{sloc},{type},{height},{width},,{height},{width}".format(
                albumid=d["albumid"], lloc=d["lloc"], sloc=d["sloc"],
                type=d["type"], height=d["height"], width=d["width"],
            )
        )
        match = re.search(r"bo=([^&]+)", d.get("url", ""))
        pic_bos.append(match.group(1) if match else "")
    return {"richval": "\t".join(richvals), "pic_bo": "\t".join(pic_bos)}


def build_publish_image_params(target_qq: int, content: str, richval: str,
                               pic_bo: str) -> Dict[str, Any]:
    """构建发表图片/图文说说的请求参数（content 为空即纯图片说说）"""
    params = {
        "syn_tweet_verson": 1,
        "paramstr": 1,
        "who": 1,
        "con": content,          # 说说文字（可为空）
        "feedversion": 1,
        "ver": 1,
        "ugc_right": 1,
        "to_sign": 0,
        "hostuin": target_qq,    # 操作QQ
        "code_version": 1,
        "format": "fs",
        "richtype": 1,           # 富文本类型：图片
        "richval": richval,      # 图片 richval
        "pic_bo": pic_bo,        # 图片 bo 参数
        "richflag": 1,
        "pic_template": "",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}",
    }
    return params


def build_comment_ugc_params(target_qq: int, uin: int, fid: str, content: str,
                             image_urls: Optional[List[str]] = None) -> Dict[str, Any]:
    """构建发表评论（emotion_cgi_addcomment_ugc，支持纯文字/图文混合）的参数。

    fid 可传说说 tid（自动补全为 ``{target_qq}_{fid}``）或完整 topicId；
    image_urls 为图片直链列表（取自 :meth:`upload_image` 返回的 ``data['url']``）。
    """
    topic_id = fid if "_" in str(fid) else f"{target_qq}_{fid}"
    params = {
        "uin": uin,               # 操作QQ
        "hostUin": target_qq,     # 说说主人QQ
        "topicId": topic_id,      # {主人QQ}_{tid}
        "commentUin": uin,        # 评论者QQ
        "content": content,       # 评论文字
        "richtype": "",           # 无图片时为空
        "richval": "",            # 无图片时为空
        "private": 0,
        "with_fwd": 0,
        "to_tweet": 0,
        "hostuin": target_qq,
        "code_version": 1,
        "format": "fs",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}",
    }
    if image_urls:
        params["richtype"] = 1
        params["richval"] = "\t".join(image_urls)
    return params


def build_reply_params(target_qq: int, uin: int, fid: str, comment_id: int,
                       content: str, image_urls: Optional[List[str]] = None) -> Dict[str, Any]:
    """构建回复评论（emotion_cgi_addreply_ugc）的参数。

    comment_id 为被回复评论的 id（取自评论返回结果的 ``data['id']``）。
    """
    topic_id = fid if "_" in str(fid) else f"{target_qq}_{fid}"
    params = {
        "uin": uin,               # 操作QQ
        "hostUin": target_qq,     # 说说主人QQ
        "topicId": topic_id,      # {主人QQ}_{tid}
        "commentId": comment_id,  # 被回复的评论ID
        "commentUin": uin,        # 回复者QQ
        "content": content,       # 回复文字
        "private": 0,
        "with_fwd": 0,
        "to_tweet": 0,
        "hostuin": target_qq,
        "code_version": 1,
        "format": "fs",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}",
    }
    if image_urls:
        params["richtype"] = 1
        params["richval"] = "\t".join(image_urls)
    return params


def build_delete_params(uin: int, fid: str, curkey: str, timestamp: int) -> Dict[str, Any]:
    """构建删除说说（emotion_cgi_delete_v6）的请求参数。

    fid 可传说说的 feedsKey（说说列表里该条的 ``cur_key``），会自动补全为官方
    要求的 topicId 形式 ``{uin}_{feedsKey}__1``；也可直接传完整 topicId。
    curkey 为 feedsKey，留空时从 fid 反推。timestamp 取说说的 ``timestamp``。
    """
    fid = str(fid)
    if "_" in fid:
        topic_id = fid
        feeds_key = curkey or fid.split("_", 1)[1].split("__", 1)[0]
    else:
        feeds_key = curkey or fid
        topic_id = f"{uin}_{feeds_key}__1"
    params = {
        "uin": uin,              # 目标QQ
        "topicId": topic_id,     # 说说topicId：{uin}_{feedsKey}__1
        "feedsType": 0,          # 说说类型
        "feedsFlag": 0,          # 说说标记
        "feedsKey": feeds_key,   # feedsKey（说说列表里的 cur_key）
        "feedsAppid": 311,
        "feedsTime": timestamp,  # 说说发布时间戳
        "fupdate": 1,            # 更新标记
        "ref": "feeds",
        "qzreferrer": f"https://user.qzone.qq.com/{uin}",
    }
    return params


def build_forward_params(uin: int, opuin: int, tid: str, content: str) -> Dict[str, Any]:
    """构建转发说说的请求参数"""
    params = {
        "t1_uin": uin,           # 目标QQ
        "t1_source": 1,          # 来源
        "tid": tid,              # 说说ID
        "signin": 0,             # 签名
        "con": content,          # 内容
        "with_cmt": 0,           # 评论
        "fwdToWeibo": 0,         # 转发到微博
        "forward_source": 2,     # 转发来源
        "code_version": 1,       # 版本
        "format": "fs",          # 返回格式
        "hostuin": opuin,        # 操作QQ
        "qzreferrer": f"https://user.qzone.qq.com/{uin}"
    }
    return params


def build_album_list_params(host_uin: int, uin: int, g_tk: int,
                            page: int = 0, count: int = 30) -> Dict[str, Any]:
    """构建获取相册列表（fcg_list_album_v3）的请求参数。

    host_uin 为要查看的相册主人QQ（可为自己或他人）；uin 为当前登录QQ。
    仅能拿到当前账号有访问权限的相册；无权限/加密相册由服务端返回受限状态。
    """
    params = {
        "g_tk": g_tk,
        "hostUin": host_uin,          # 相册主人QQ
        "uin": uin,                   # 当前登录QQ
        "appid": 4,
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "source": "qzone",
        "plat": "qzone",
        "format": "jsonp",
        "notice": 0,
        "filter": 1,
        "handset": 4,
        "pageNumModeSort": 40,
        "pageNumModeClass": 15,
        "needUserInfo": 1,
        "idcNum": 4,
        "callbackFun": "shine0",
        "callback": "shine0_Callback",
        "pageStart": page * count,    # 起始位置
        "pageNum": count,             # 拉取数量
    }
    return params


def build_album_photo_params(host_uin: int, uin: int, album_id: str, g_tk: int,
                             page: int = 0, count: int = 30) -> Dict[str, Any]:
    """构建获取相册内图片列表（cgi_list_photo）的请求参数。

    album_id 取自 :func:`build_album_list_params` 返回的相册 ``id``。
    无权访问的相册服务端会直接返回错误，不下发图片数据。
    """
    params = {
        "g_tk": g_tk,
        "hostUin": host_uin,          # 相册主人QQ
        "uin": uin,                   # 当前登录QQ
        "topicId": album_id,          # 相册ID
        "appid": 4,
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "source": "qzone",
        "plat": "qzone",
        "format": "jsonp",
        "notice": 0,
        "filter": 1,
        "handset": 4,
        "pageStart": page * count,    # 起始位置
        "pageNum": count,             # 每页数量
        "sortOrder": 2,
        "need_private_comment": 1,
        "callbackFun": "shine0",
        "callback": "shine0_Callback",
    }
    return params


def build_delete_photo_params(uin: int, album_id: str, lloc: str, sloc: str,
                              priv: int = 1) -> Dict[str, Any]:
    """构建删除自己相册中某张图片的请求参数（cgi_delpic_multi_v2，只能删自己名下的图片）。

    lloc/sloc/priv 取自 :meth:`list_album_photos` / :meth:`list_albums` 返回的字段；
    codelist 为待删图片列表，单张格式为 ``{lloc}|53|0|0||{sloc}|{priv}|0``。
    """
    codelist = f"{lloc}|53|0|0||{sloc}|{priv}|0"
    params = {
        "qzreferrer": f"https://user.qzone.qq.com/{uin}",
        "albumid": album_id,          # 相册ID
        "nvip": 1,
        "priv": priv,                 # 相册权限（取自相册的 rights）
        "codelist": codelist,         # 待删图片定位串列表
        "ismultiup": 0,
        "resetcover": 1,
        "newcover": "",
        "uin": uin,                   # 当前登录QQ（须为图片主人）
        "hostUin": uin,
        "plat": "qzone",
        "source": "qzone",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
    }
    return params


def build_delcomment_ugc_params(target_qq: int, uin: int, fid: str,
                                comment_id: int) -> Dict[str, Any]:
    """构建删除说说评论（emotion_cgi_delcomment_ugc）的参数。

    comment_id 为要删除评论的 id（说说列表里评论的 ``id``，或发表评论返回的 ``data['id']``）。
    """
    topic_id = fid if "_" in str(fid) else f"{target_qq}_{fid}"
    return {
        "uin": uin,               # 操作QQ
        "hostUin": target_qq,     # 说说主人QQ
        "topicId": topic_id,      # {主人QQ}_{tid}
        "commentId": comment_id,  # 要删除的评论ID
        "commentUin": uin,        # 操作者QQ
        "hostuin": target_qq,
        "code_version": 1,
        "format": "fs",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}",
    }


def build_delreply_ugc_params(target_qq: int, uin: int, fid: str, comment_id: int,
                              reply_id: int) -> Dict[str, Any]:
    """构建删除评论回复（emotion_cgi_delreply_ugc）的参数。

    comment_id 为回复所属评论 id，reply_id 为要删除回复的 id。
    """
    topic_id = fid if "_" in str(fid) else f"{target_qq}_{fid}"
    return {
        "uin": uin,               # 操作QQ
        "hostUin": target_qq,     # 说说主人QQ
        "topicId": topic_id,      # {主人QQ}_{tid}
        "commentId": comment_id,  # 回复所属评论ID
        "replyId": reply_id,      # 要删除的回复ID
        "commentUin": uin,        # 操作者QQ
        "hostuin": target_qq,
        "code_version": 1,
        "format": "fs",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}",
    }


def build_comment_like_params(opuin: int, host_qq: int, tid: str,
                              comment_id: int) -> Dict[str, Any]:
    """构建点赞说说评论（internal_dolike_app）的参数。

    curkey/unikey 指向评论对象 ``{host}_{tid}_{comment_id}``。
    """
    curkey = f"{host_qq}_{tid}_{comment_id}"
    return {
        "qzreferrer": f"https://user.qzone.qq.com/{opuin}",
        "opuin": opuin,           # 操作者QQ
        "unikey": curkey,         # 评论唯一标识
        "curkey": curkey,         # 操作对象
        "appid": 311,
        "from": -100,
        "typeid": 0,
        "abstime": int(time.time()),
        "fid": tid,
        "active": 0,
        "fupdate": 1,
        "face": 0,
        "format": "json",
    }


def build_message_board_params(host_qq: int, uin: int, g_tk: int,
                               start: int = 0, num: int = 10) -> Dict[str, Any]:
    """构建获取留言板留言列表（get_msgb）的请求参数（g_tk 用 p_skey 计算）。"""
    return {
        "uin": host_qq,           # 留言板主人QQ
        "hostUin": host_qq,       # 留言板主人QQ
        "hostword": 0,
        "start": start,           # 起始位置
        "s": num,                 # 拉取数量
        "num": num,
        "essence": 1,
        "r": 0,
        "format": "jsonp",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "ref": "qzone",
        "g_tk": g_tk,
    }


def build_add_message_board_params(host_qq: int, uin: int, content: str) -> Dict[str, Any]:
    """构建发表留言（add_msgb）的请求参数（g_tk 用 p_skey 计算）。"""
    return {
        "uin": uin,               # 操作QQ
        "hostUin": host_qq,       # 留言板主人QQ
        "format": "fs",
        "iNotice": 1,
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "ref": "qzone",
        "json": 1,
        "content": content,       # 留言内容
        "signin": 1,
        "qzreferrer": f"https://user.qzone.qq.com/{host_qq}",
    }


def build_del_message_board_params(host_qq: int, msg_id: int,
                                   author_uin: int) -> Dict[str, Any]:
    """构建删除留言（del_msgb）的请求参数（g_tk 用 p_skey 计算）。

    msg_id 取自 :func:`build_message_board_params` 返回留言的 ``id``；
    author_uin 为该留言留言者的 QQ（返回里的 ``uin``）。
    """
    return {
        "hostUin": host_qq,       # 留言板主人QQ
        "idList": msg_id,         # 要删除的留言ID（多个用逗号连接）
        "uinList": author_uin,    # 对应留言者QQ（多个用逗号连接）
        "format": "fs",
        "iNotice": 1,
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "ref": "qzone",
        "json": 1,
        "qzreferrer": f"https://user.qzone.qq.com/{host_qq}",
    }


def build_visitor_params(uin: int, g_tk: int, mask: int = 2,
                         page: int = 1, count: int = 20) -> Dict[str, Any]:
    """构建获取空间访客列表（cgi_get_visitor_simple）的请求参数（g_tk 用 p_skey 计算）。"""
    return {
        "uin": uin,               # 自己的QQ
        "mask": mask,
        "page": page,
        "fupdate": 1,
        "clear": 1,
        "g_tk": g_tk,
    }


def build_blog_list_params(host_qq: int, uin: int, g_tk: int,
                           pos: int = 0, num: int = 15) -> Dict[str, Any]:
    """构建获取日志列表（get_abs）的请求参数（g_tk 用 p_skey 计算）。"""
    return {
        "hostUin": host_qq,       # 日志主人QQ
        "uin": uin,               # 当前登录QQ
        "blogType": 0,
        "cateName": "",
        "cateHex": "",
        "statYear": "",
        "reqInfo": 3,             # 3 才会返回日志明细 list
        "pos": pos,               # 起始位置
        "num": num,               # 拉取数量
        "sortType": 0,
        "source": 0,
        "g_tk": g_tk,
        "format": "jsonp",
    }


def build_blog_add_params(uin: int, title: str, content: str,
                          right_type: int = 1, category: str = "个人日记"
                          ) -> Dict[str, Any]:
    """构建发表日志（add_blog）的请求参数（g_tk 用 p_skey 计算）。

    right_type 权限：1 公开 / 2 QQ好友 / 3 指定人 / 4 仅自己。
    """
    return {
        "cate": category,         # 日志分类
        "title": title,          # 标题
        "html": content,         # 正文HTML
        "para": "",
        "blogType": 0,
        "lp_type": 0,
        "lp_flag": 0,
        "autograph": 1,
        "topFlag": 0,
        "feeds": 1,
        "tweetFlag": 0,
        "rightType": right_type,  # 可见范围
        "uin": uin,
        "hostUin": uin,
        "iNotice": 1,
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "format": "fs",
        "ref": "qzone",
        "json": 1,
        "qzreferrer": f"https://user.qzone.qq.com/{uin}/infocenter",
    }


def build_blog_mod_params(uin: int, blog_id: int, title: str, content: str,
                          right_type: int = 1, category: str = "个人日记"
                          ) -> Dict[str, Any]:
    """构建编辑日志（mod_blog）的请求参数（g_tk 用 p_skey 计算）。

    blog_id 取自 :func:`build_blog_list_params` 返回列表里日志的 ``blogId``。
    """
    params = build_blog_add_params(uin, title, content, right_type, category)
    params["blogId"] = blog_id    # 要编辑的日志ID
    params["feeds"] = 0
    return params


def build_blog_del_params(uin: int, host_qq: int, blog_id: int) -> Dict[str, Any]:
    """构建删除日志（del_blog）的请求参数（g_tk 用 p_skey 计算）。

    blog_id 可传单个 id；多个用下划线连接的字符串传给 idList。
    """
    return {
        "uin": uin,               # 当前登录QQ
        "hostUin": host_qq,       # 日志主人QQ
        "idList": str(blog_id),   # 日志ID（多个用 _ 连接）
        "blogType": 0,
        "incharset": "utf-8",
        "outcharset": "utf-8",
        "format": "fs",
        "ref": "qzone",
        "json": 1,
        "qzreferrer": f"https://user.qzone.qq.com/{host_qq}/infocenter",
    }


# ---- 兼容别名（旧版本函数名） ----
like_feed = build_like_params
get_feeds = build_friend_feeds_params
get_self_zone = build_messages_params
get_send_zone = build_publish_params
get_send_comment = build_comment_params
get_del_zone = build_delete_params
get_forward_zone = build_forward_params
