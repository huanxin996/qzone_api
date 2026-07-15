from typing import Dict, Any, Optional
from loguru import logger
from .api_base import ApiBase
from .api_parms import (
    build_friend_feeds_params,
    build_messages_params,
    build_album_list_params,
    build_album_photo_params,
    build_message_board_params,
    build_visitor_params,
    build_blog_list_params,
)
from ..utils import parse_callback_data, parse_feeds, parse_feed_data, clean_escaped_html


class ApiZone(ApiBase):
    """空间动态/说说列表相关 API"""

    def __init__(self):
        self.self_url = "https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6"
        self.user_url = "https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds3_html_more"
        self.dolike_url = "https://user.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/likes/internal_dolike_app"
        self.send_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6"
        self.dell_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_delete_v6"
        self.send_comments_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_re_feeds"
        self.forward_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_forward_v6"
        self.upload_url = "https://up.qzone.qq.com/cgi-bin/upload/cgi_upload_image"
        self.comment_ugc_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_addcomment_ugc"
        self.reply_ugc_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_addreply_ugc"
        self.album_list_url = "https://h5.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/fcg_list_album_v3"
        self.album_photo_url = "https://h5.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/cgi_list_photo"
        self.delete_photo_url = "https://user.qzone.qq.com/proxy/domain/photo.qzone.qq.com/cgi-bin/common/cgi_delpic_multi_v2"
        self.update_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_update"
        self.delcomment_ugc_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_delcomment_ugc"
        self.delreply_ugc_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_delreply_ugc"
        self.msgb_get_url = "https://user.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/get_msgb"
        self.msgb_add_url = "https://user.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/add_msgb"
        self.msgb_del_url = "https://h5.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/del_msgb"
        self.visitor_url = "https://user.qzone.qq.com/proxy/domain/g.qzone.qq.com/cgi-bin/friendshow/cgi_get_visitor_simple"
        self.blog_add_url = "https://rc.qzone.qq.com/proxy/domain/b.qzone.qq.com/cgi-bin/blognew/add_blog"
        self.blog_mod_url = "https://rc.qzone.qq.com/proxy/domain/b.qzone.qq.com/cgi-bin/blognew/mod_blog"
        self.blog_del_url = "https://rc.qzone.qq.com/proxy/domain/b.qzone.qq.com/cgi-bin/blognew/del_blog"
        self.blog_list_url = "https://rc.qzone.qq.com/proxy/domain/b.qzone.qq.com/cgi-bin/blognew/get_abs"

    async def fetch_friend_feeds_raw(self, target_qq: int, g_tk: int, cookies: str,
                                     page: int = 1, count: int = 10,
                                     begintime: int = 0) -> Optional[str]:
        """获取好友动态原始响应文本"""
        try:
            params = build_friend_feeds_params(target_qq, g_tk, page=page, count=count, begintime=begintime)
            return await self._make_get_request(self.user_url, params, cookies)
        except Exception as e:
            logger.error(f"获取空间动态失败: {e}")
            return None

    async def get_friend_feeds(self, target_qq: int, g_tk: int, cookies: str,
                               page: int = 1, count: int = 10,
                               begintime: int = 0) -> Optional[Dict[str, Any]]:
        """获取好友动态并解析为结构化数据"""
        content = await self.fetch_friend_feeds_raw(target_qq, g_tk, cookies, page, count, begintime)
        if content:
            return parse_feeds(content)
        return None

    async def fetch_messages_raw(self, target_qq: int, g_tk: int, cookies: str,
                                 pos: int = 0, num: int = 20,
                                 begintime: int = 0) -> Optional[str]:
        """获取指定QQ说说列表原始响应文本"""
        try:
            params = build_messages_params(target_qq, g_tk, pos, num, begintime)
            return await self._make_get_request(self.self_url, params, cookies)
        except Exception as e:
            logger.error(f"获取说说列表失败: {e}")
            return None

    async def get_messages_list(self, target_qq: int, g_tk: int, cookies: str,
                                pos: int = 0, num: int = 20,
                                begintime: int = 0) -> Optional[Dict[str, Any]]:
        """获取指定QQ的说说列表并解析为结构化数据"""
        content = await self.fetch_messages_raw(target_qq, g_tk, cookies, pos, num, begintime)
        if content:
            data = parse_callback_data(clean_escaped_html(content))
            if data is not None:
                return parse_feed_data(data)
        return None

    async def list_albums(self, host_qq: int, uin: int, g_tk: int, cookies: str,
                          page: int = 0, count: int = 30) -> Optional[Dict[str, Any]]:
        """获取相册列表并解析为结构化数据。

        host_qq 为相册主人QQ（自己或他人），uin 为当前登录QQ。
        只会返回当前账号有权访问的相册；无权限/加密相册服务端返回受限状态。
        """
        params = build_album_list_params(host_qq, uin, g_tk, page=page, count=count)
        content = await self._make_get_request(self.album_list_url, params, cookies)
        if not content:
            return None
        data = self._extract_json(content)
        if data is None:
            logger.error("相册列表解析失败")
            return None
        return self._parse_album_list(data)

    async def list_album_photos(self, host_qq: int, uin: int, album_id: str, g_tk: int,
                                cookies: str, page: int = 0, count: int = 30
                                ) -> Optional[Dict[str, Any]]:
        """获取指定相册内的图片列表并解析为结构化数据。

        album_id 取自 :meth:`list_albums` 返回的相册 ``id``。
        无权访问的相册服务端会直接返回错误。
        """
        params = build_album_photo_params(host_qq, uin, album_id, g_tk, page=page, count=count)
        content = await self._make_get_request(self.album_photo_url, params, cookies)
        if not content:
            return None
        data = self._extract_json(content)
        if data is None:
            logger.error("相册图片列表解析失败")
            return None
        return self._parse_album_photos(data)

    @staticmethod
    def _parse_album_list(data: Dict[str, Any]) -> Dict[str, Any]:
        """将相册列表原始响应整理为结构化数据"""
        if data.get("code") != 0:
            return {"status": "error", "code": data.get("code"),
                    "message": data.get("message", ""), "albums": []}
        body = data.get("data") or {}
        albums = []
        for a in (body.get("albumListModeSort") or body.get("albumList") or []):
            albums.append({
                "id": a.get("id", ""),
                "name": a.get("name", ""),
                "desc": a.get("desc", ""),
                "photo_count": a.get("total", 0),
                "cover": a.get("pre", ""),
                "created": a.get("createtime", 0),
                "modified": a.get("modifytime", 0),
                "rights": a.get("priv", 0),          # 权限：1公开/其他为受限
                "is_locked": bool(a.get("lockright", 0)),  # 是否加密/需密码
            })
        return {"status": "ok", "total": body.get("albumsInUser", len(albums)), "albums": albums}

    @staticmethod
    def _parse_album_photos(data: Dict[str, Any]) -> Dict[str, Any]:
        """将相册图片列表原始响应整理为结构化数据"""
        if data.get("code") != 0:
            return {"status": "error", "code": data.get("code"),
                    "message": data.get("message", ""), "photos": []}
        body = data.get("data") or {}
        photos = []
        for p in (body.get("photoList") or []):
            photos.append({
                "lloc": p.get("lloc", ""),           # 图片定位串（删除时用）
                "sloc": p.get("sloc", ""),
                "name": p.get("name", ""),
                "desc": p.get("desc", ""),
                "url": p.get("url", "") or p.get("origin_url", ""),
                "origin_url": p.get("origin_url", ""),
                "width": p.get("width", 0),
                "height": p.get("height", 0),
                "uploadtime": p.get("uploadtime", ""),
            })
        return {"status": "ok", "total": body.get("totalInAlbum", len(photos)),
                "album_id": body.get("topic", {}).get("id", "") if isinstance(body.get("topic"), dict) else "",
                "photos": photos}

    async def get_message_board(self, host_qq: int, uin: int, g_tk: int, cookies: str,
                                start: int = 0, num: int = 10) -> Optional[Dict[str, Any]]:
        """获取留言板留言列表并解析（g_tk 用 p_skey 计算）。

        host_qq 为留言板主人QQ，uin 为当前登录QQ；只返回有权访问的留言。
        """
        params = build_message_board_params(host_qq, uin, g_tk, start=start, num=num)
        content = await self._make_get_request(self.msgb_get_url, params, cookies)
        if not content:
            return None
        data = self._extract_json(content)
        if data is None:
            logger.error("留言板解析失败")
            return None
        return self._parse_message_board(data)

    async def get_visitors(self, uin: int, g_tk: int, cookies: str,
                           page: int = 1, count: int = 20) -> Optional[Dict[str, Any]]:
        """获取空间访客列表并解析（g_tk 用 p_skey 计算，只能查自己的访客）。"""
        params = build_visitor_params(uin, g_tk, page=page, count=count)
        content = await self._make_get_request(self.visitor_url, params, cookies)
        if not content:
            return None
        data = self._extract_json(content)
        if data is None:
            logger.error("访客列表解析失败")
            return None
        return self._parse_visitors(data)

    async def list_blogs(self, host_qq: int, uin: int, g_tk: int, cookies: str,
                         pos: int = 0, num: int = 15) -> Optional[Dict[str, Any]]:
        """获取日志列表并解析（g_tk 用 p_skey 计算）。

        host_qq 为日志主人QQ，uin 为当前登录QQ；每条含 ``blogId`` 可用于编辑/删除。
        """
        params = build_blog_list_params(host_qq, uin, g_tk, pos=pos, num=num)
        content = await self._make_get_request(self.blog_list_url, params, cookies)
        if not content:
            return None
        data = self._extract_json(content)
        if data is None:
            logger.error("日志列表解析失败")
            return None
        return self._parse_blog_list(data)

    @staticmethod
    def _parse_message_board(data: Dict[str, Any]) -> Dict[str, Any]:
        """整理留言板原始响应为结构化数据"""
        if data.get("code") != 0:
            return {"status": "error", "code": data.get("code"),
                    "message": data.get("message", ""), "messages": []}
        body = data.get("data") or {}
        messages = []
        for m in (body.get("commentList") or []):
            messages.append({
                "id": m.get("id", 0),                # 留言ID（删除时用）
                "uin": m.get("uin", 0),              # 留言者QQ
                "name": m.get("nickname", ""),       # 留言者昵称
                "content": m.get("htmlContent", m.get("ubbContent", m.get("content", ""))),  # 留言内容
                "time": m.get("pubtime", ""),        # 留言时间
                "secret": bool(m.get("secret", 0)),  # 是否私密留言
                "reply_count": len(m.get("replyList") or []),
            })
        return {"status": "ok", "total": body.get("total", len(messages)),
                "messages": messages}

    @staticmethod
    def _parse_visitors(data: Dict[str, Any]) -> Dict[str, Any]:
        """整理访客原始响应为结构化数据"""
        if data.get("code") != 0:
            return {"status": "error", "code": data.get("code"),
                    "message": data.get("message", ""), "visitors": []}
        body = data.get("data") or {}
        visitors = []
        for v in (body.get("items") or []):
            visitors.append({
                "uin": v.get("uin", 0),              # 访客QQ
                "name": v.get("name", ""),           # 访客昵称
                "time": v.get("time", 0),            # 来访时间戳
                "is_friend": bool(v.get("isFriend", 0)),  # 是否好友
                "avatar": v.get("img", ""),          # 头像URL
            })
        return {"status": "ok",
                "count": body.get("count", len(visitors)),      # 本次返回访客数
                "total_visit": body.get("calvisitcount", 0),    # 累计访问量
                "visitors": visitors}

    @staticmethod
    def _parse_blog_list(data: Dict[str, Any]) -> Dict[str, Any]:
        """整理日志列表原始响应为结构化数据"""
        if data.get("code") != 0:
            return {"status": "error", "code": data.get("code"),
                    "message": data.get("message", ""), "blogs": []}
        body = data.get("data") or {}
        blogs = []
        for b in (body.get("list") or []):
            blogs.append({
                "blogId": b.get("blogId", b.get("blogid", 0)),  # 日志ID（编辑/删除用）
                "title": b.get("title", ""),         # 标题
                "time": b.get("pubTime", b.get("pubtime", "")),  # 发表时间
                "comment_count": b.get("commentNum", 0),  # 评论数
                "category": b.get("cate", ""),       # 分类
            })
        return {"status": "ok", "total": body.get("totalNum", len(blogs)),
                "blogs": blogs}

    # ---- 兼容别名（旧版本方法名） ----
    _get_zone = fetch_friend_feeds_raw
    _get_messages_list = fetch_messages_raw
