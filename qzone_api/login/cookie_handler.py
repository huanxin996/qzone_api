import time,asyncio,requests,re
from loguru import logger
from ..utils import bkn, ptqrToken

class CookieHandler:
    def __init__(self):
        self.cookies = None
        
    async def get_cookies(self, qrsig):
        ptqrtoken = ptqrToken(qrsig)
        
        while True:
            status = await self._check_login_status(qrsig, ptqrtoken)
            if status.get("success"):
                return status.get("cookies")
            elif status.get("expired"):
                return None
                
            await asyncio.sleep(3)
            
    async def _check_login_status(self, qrsig, ptqrtoken):
        url = f'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=https%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&ptqrtoken={ptqrtoken}&ptredirect=0&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-{time.time()}&js_ver=20032614&js_type=1&login_sig=&pt_uistyle=40&aid=549000912&daid=5&'
        
        try:
            r = requests.get(url, cookies={'qrsig': qrsig})
            return self._parse_response(r)
        except Exception as e:
            logger.debug(f"检查登录状态失败: {e}")
            return {"success": False}
    
    def _parse_response(self, response):
        """解析QQ登录响应"""
        text = response.text
        
        if '二维码未失效' in text:
            return {"success": False, "expired": False}
            
        elif '二维码认证中' in text:
            logger.debug('二维码认证中')
            return {"success": False, "expired": False}
            
        elif '二维码已失效' in text:
            logger.debug('二维码已失效')
            return {"success": False, "expired": True}
            
        elif '登录成功' in text:
            logger.debug('登录成功')
            cookies = requests.utils.dict_from_cookiejar(response.cookies)
            uin = cookies.get('uin')
            regex = re.compile(r'ptsigx=(.*?)&')
            sigx = re.findall(regex, text)[0]
            url = (f'https://ptlogin2.qzone.qq.com/check_sig?pttype=1&uin={uin}'
                f'&service=ptqrlogin&nodirect=0&ptsigx={sigx}'
                '&s_url=https%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html'
                '%3Fpara%3Dizone&f_url=&ptlang=2052&ptredirect=100&aid=549000912'
                '&daid=5&j_later=0&low_login_hour=0&regmaster=0&pt_login_type=3'
                '&pt_aid=0&pt_aaid=16&pt_light=0&pt_3rd_aid=0') 
            try:
                r = requests.get(url, cookies=cookies, allow_redirects=False)
                target_cookies = requests.utils.dict_from_cookiejar(r.cookies)
                return {"success": True, "cookies": target_cookies} 
            except Exception as e:
                logger.debug(f"获取最终cookies失败: {e}")
                return {"success": False, "expired": False}
        else:
            logger.debug('用户取消登录')
            return {"success": False, "expired": True}