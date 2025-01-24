from typing import Dict, Any, Optional
from loguru import logger
from .api_base import ApiBase
from .api_parms import *
from ..utils import *

class ApiZone(ApiBase):
    def __init__(self):
        self.self_url = "https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6"
        self.user_url = "https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds3_html_more"
        self.dolike_url = "https://user.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/likes/internal_dolike_app"
        self.send_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6"
        self.dell_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_delete_v6"
        self.send_comments_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_re_feeds"
        self.forward_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_forward_v6"

    async def _get_zone(self, target_qq: int, g_tk: int, cookies: str,page:int=1,count:int=10,begintime:int=0) -> Optional[Dict[str, Any]]:
        """获取空间动态"""
        try:
            # 获取动态参数
            params = get_feeds(target_qq, g_tk,page=page,count=count,begintime=begintime)
            return await self._make_get_request(self.user_url, params, cookies)
        except Exception as e:
            logger.error(f"获取空间动态失败: {e}")
            return None
    async def _get_messages_list(self, target_qq: int, g_tk: int, cookies: str, pos: int = 0, num: int = 20) -> Optional[Dict[str, Any]]:
        """获取说说列表原始数据"""
        try:
            params = get_self_zone(target_qq, g_tk, pos, num)
            return await self._make_get_request(self.self_url, params, cookies)
        except Exception as e:
            logger.error(f"获取说说列表失败: {e}")
            return None
    
    async def get_messages_list(self, target_qq: int, g_tk: int, cookies: str, pos: int = 0, num: int = 20) -> Optional[Dict[str, Any]]:
        """获取说说列表"""
        connect = await self._get_messages_list(target_qq, g_tk, cookies, pos, num)
        if connect:
            return parse_feed_data(parse_callback_data(clean_escaped_html(connect)))
        return None