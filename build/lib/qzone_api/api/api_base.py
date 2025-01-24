import aiohttp
import json
import re
from typing import Dict, Any, Optional
from loguru import logger

class ApiBase:
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
        except Exception as e:
            logger.error(f"请求异常: {e}")
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