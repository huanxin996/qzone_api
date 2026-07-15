"""QQ空间各接口的请求参数构建函数。

命名规范：所有参数构建函数以 ``build_`` 开头，返回可直接用于请求的 dict。
旧函数名（like_feed/get_feeds/get_self_zone/get_send_zone/get_send_comment/
get_del_zone/get_forward_zone）作为兼容别名保留。
"""
import re
import time
from typing import Dict, Any, List, Optional


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


def build_publish_params(target_qq: int, content: str) -> Dict[str, Any]:
    """构建发表文本说说的请求参数"""
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
        "ugc_right": 1,          # 权限
        "to_sign": 0,            # 签名
        "code_version": 1,
        "format": "fs",
        "qzreferrer": f"https://user.qzone.qq.com/{target_qq}"
    }
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
    """构建删除说说的请求参数"""
    params = {
        "uin": uin,              # 目标QQ
        "topicId": fid,          # 说说ID
        "feedsType": 0,          # 说说类型
        "feedsFlag": 0,          # 说说标记
        "feedsKey": curkey,      # 当前key
        "feedsAppid": 311,
        "feedsTime": timestamp,  # 时间戳
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


# ---- 兼容别名（旧版本函数名） ----
like_feed = build_like_params
get_feeds = build_friend_feeds_params
get_self_zone = build_messages_params
get_send_zone = build_publish_params
get_send_comment = build_comment_params
get_del_zone = build_delete_params
get_forward_zone = build_forward_params
