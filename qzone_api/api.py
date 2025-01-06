import aiohttp,json,re
from typing import Dict, Any, Optional
from loguru import logger
from .parms import *

class QzoneApi:
    def __init__(self):
        self.self_url = "https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6"
        self.user_url = "https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds3_html_more"
        self.dolike_url = "https://user.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/likes/internal_dolike_app"
        self.send_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6"
        self.dell_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_delete_v6"
        self.send_comments_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_re_feeds"
        self.forward_url = "https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_forward_v6"
        #拼尽全力无法战胜上传图像
        self.test_url = "https://up.qzone.qq.com/cgi-bin/upload/cgi_upload_image?g_tk=781338046&"
    

    async def _make_post_request(self, url: str, data: Dict[str, Any], cookies: str, content_type: str = 'application/x-www-form-urlencoded') -> Optional[Dict[str, Any]]:
        """通用POST请求方法"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": cookies,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": content_type,
            "Origin": "https://user.qzone.qq.com",
            "Referer": "https://user.qzone.qq.com/"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"POST响应内容: {content[:100]}")
                        if 'text/html' in response.headers.get('Content-Type', ''):
                            match = re.search(r'({.*})', content)
                            if match:
                                try:
                                    return json.loads(match.group(1))
                                except json.JSONDecodeError:
                                    pass
                            match = re.search(r'_Callback\((.*)\);', content)
                            if match:
                                try:
                                    return json.loads(match.group(1))
                                except json.JSONDecodeError:
                                    pass
                        return content
                    logger.error(f"POST请求失败: {response.status}")
                    return None  
        except aiohttp.ClientError as e:
            logger.error(f"POST请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"其他异常: {e}")
            return None
    
    async def _make_get_request(self, url: str, params: Dict[str, Any], cookies: str) -> Optional[Dict[str, Any]]:
        """通用GET请求方法"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": cookies,
            "Accept": "application/json, text/plain, */*"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"原始响应内容: {content[:100]}")
                        return content
                    logger.error(f"请求失败状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return None

    async def get_zone(self, target_qq: str, g_tk: str, cookies: str,page:int=1,count:int=10,begintime:int=0) -> Optional[Dict[str, Any]]:
        """获取空间动态"""
        try:
            # 获取动态参数
            params = get_feeds(target_qq, g_tk,page=page,count=count,begintime=begintime)
            return await self._make_get_request(self.user_url, params, cookies)
        except Exception as e:
            logger.error(f"获取空间动态失败: {e}")
            return None

    async def get_messages_list(self, target_qq: str, g_tk: str, cookies: str, pos: int = 0, num: int = 20) -> Optional[Dict[str, Any]]:
        """获取说说列表"""
        try:
            params = get_self_zone(target_qq, g_tk, pos, num)
            return await self._make_get_request(self.self_url, params, cookies)
        except Exception as e:
            logger.error(f"获取说说列表失败: {e}")
            return None
        
    async def zanzone(self, target_qq: int, g_tk: str, fid: int, cur_key: str,uni_key:str,cookies: str) -> Optional[Dict[str, Any]]:
        """点赞指定说说"""
        try:
            params = like_feed(opuin=target_qq,fid=fid, cur_key=cur_key,uni_key=uni_key)
            logger.info(params)
            return await self._make_post_request(url=f"{self.dolike_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"尝试点赞时失败: {e}")
            return None

    async def send_zone(self, target_qq: str, content: str, cookies: str,g_tk:str) -> Optional[Dict[str, Any]]:
        """发送文本说说"""
        try:
            params = get_send_zone(target_qq, content)
            return await self._make_post_request(url=f"{self.send_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发送说说失败: {e}")
            return None
    
    async def send_comments(self, target_qq: int,uin:int, content: str, cookies: str,g_tk:str,fid:str) -> Optional[Dict[str, Any]]:
        """发送评论"""
        try:
            params = get_send_comment(target_qq,uin, content,fid)
            return await self._make_post_request(url=f"{self.send_comments_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发送说说失败: {e}")
            return None

    async def del_zone(self, target_qq: str, fid: str, cookies: str,g_tk:str,curkey:str,timestamp:int) -> Optional[Dict[str, Any]]:
        """删除说说"""
        try:
            params = get_del_zone(target_qq, fid,curkey,timestamp)
            return await self._make_post_request(url=f"{self.dell_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除说说失败: {e}")
            return None
        
    async def forward_zone(self, target_qq: int,opuin:int, tid: str,connect:str, cookies: str,g_tk:str) -> Optional[Dict[str, Any]]:
        """转发说说"""
        try:
            params = get_forward_zone(target_qq, opuin,tid,connect)
            return await self._make_post_request(url=f"{self.forward_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"转发说说失败: {e}")
            return None