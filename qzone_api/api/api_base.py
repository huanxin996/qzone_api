import aiohttp
import json
import re
from typing import Dict, Any, Optional, Union
from loguru import logger

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class ApiBase:
    """封装通用的 GET/POST 请求逻辑，供各 API Mixin 继承使用"""

    def _build_headers(self, cookies: str, content_type: Optional[str] = None) -> Dict[str, str]:
        """构建请求头，content_type 不为 None 时附带 POST 所需头部"""
        headers = {
            "User-Agent": USER_AGENT,
            "Cookie": cookies,
            "Accept": "application/json, text/plain, */*",
        }
        if content_type is not None:
            headers["Content-Type"] = content_type
            headers["Origin"] = "https://user.qzone.qq.com"
            headers["Referer"] = "https://user.qzone.qq.com/"
        return headers

    @staticmethod
    def _extract_json(content: str) -> Optional[Dict[str, Any]]:
        """从 HTML/回调文本中尽力提取 JSON 对象，失败返回 None"""
        for pattern in (r'frameElement\.callback\(\s*(\{.*\})\s*\)', r'_Callback\(\s*(.*?)\s*\)', r'({.*})'):
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        return None

    async def _make_post_request(self, url: str, data: Dict[str, Any], cookies: str,
                                 content_type: str = 'application/x-www-form-urlencoded'
                                 ) -> Optional[Union[Dict[str, Any], str]]:
        """通用POST请求方法，text/html 响应时尝试提取其中的 JSON"""
        headers = self._build_headers(cookies, content_type=content_type)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"POST响应内容: {content[:100]}")
                        parsed = self._extract_json(content)
                        if parsed is not None:
                            return parsed
                        return content
                    logger.error(f"POST请求失败: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return None

    async def _make_get_request(self, url: str, params: Dict[str, Any], cookies: str) -> Optional[str]:
        """通用GET请求方法，返回原始响应文本"""
        headers = self._build_headers(cookies)
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
