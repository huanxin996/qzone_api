from typing import Dict, Any, Optional
from loguru import logger
from .api_base import ApiBase
from .api_parms import *

class ApiFeed(ApiBase):
    async def _zanzone(self, target_qq: int, g_tk: int, fid: int, cur_key: str, uni_key:str, cookies: str) -> Optional[Dict[str, Any]]:
        """点赞指定说说"""
        try:
            params = like_feed(opuin=target_qq,fid=fid, cur_key=cur_key,uni_key=uni_key)
            return await self._make_post_request(url=f"{self.dolike_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"尝试点赞时失败: {e}")
            return None

    async def _send_zone(self, target_qq: int, content: str, cookies: str, g_tk:int) -> Optional[Dict[str, Any]]:
        """发送文本说说"""
        try:
            params = get_send_zone(target_qq, content)
            return await self._make_post_request(url=f"{self.send_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发送说说失败: {e}")
            return None
    async def _forward_zone(self, target_qq: int,opuin:int, tid: str,connect:str, cookies: str,g_tk:int) -> Optional[Dict[str, Any]]:
        """转发说说"""
        try:
            params = get_forward_zone(target_qq, opuin,tid,connect)
            return await self._make_post_request(url=f"{self.forward_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"转发说说失败: {e}")
            return None
    async def _del_zone(self, target_qq: int, fid: str, cookies: str,g_tk:int,curkey:str,timestamp:int) -> Optional[Dict[str, Any]]:
        """删除说说"""
        try:
            params = get_del_zone(target_qq, fid,curkey,timestamp)
            return await self._make_post_request(url=f"{self.dell_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除说说失败: {e}")
            return None
    async def _send_comments(self, target_qq: int,uin:int, content: str, cookies: str,g_tk:str,fid:str) -> Optional[Dict[str, Any]]:
        """发送评论"""
        try:
            params = get_send_comment(target_qq,uin, content,fid)
            return await self._make_post_request(url=f"{self.send_comments_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发送说说失败: {e}")
            return None