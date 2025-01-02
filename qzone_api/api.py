import aiohttp,json,time
from typing import Dict, Any, Optional
from loguru import logger
from .parms import like_feed,get_feeds,get_self_zone

class QzoneApi:
    def __init__(self):
        self.self_url = "https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6"
        self.user_url = "https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds3_html_more"
        self.dolike_url = "https://user.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/likes/internal_dolike_app"
        self.test_url = "https://user.qzone.qq.com/proxy/domain/statistic.qzone.qq.com/cgi-bin/feeds2_oz"
    

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
                        try:
                            return await response.json()
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON解析失败: {e},请自行处理原数据")
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

    async def get_zone(self, target_qq: str, g_tk: str, cookies: str) -> Optional[Dict[str, Any]]:
        """获取空间动态"""
        try:
            # 获取动态参数
            params = get_feeds(target_qq, g_tk)
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
        
    async def zanzone(self, target_qq: str, g_tk: str, fid: int, cur_key: str,uni_key:str,cookies: str) -> Optional[Dict[str, Any]]:
        """点赞指定说说"""
        try:
            params = like_feed(opuin=target_qq,fid=fid, cur_key=cur_key,uni_key=uni_key)
            return await self._make_post_request(url=f"{self.dolike_url}?g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"尝试点赞时失败: {e}")
            return None
