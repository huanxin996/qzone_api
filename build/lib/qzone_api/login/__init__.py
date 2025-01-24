from .qrcode import QRCodeHandler
from .cookie_handler import CookieHandler,bkn
from loguru import logger

class QzoneLogin:
    def __init__(self):
        self.qr_handler = QRCodeHandler()
        self.cookie_handler = CookieHandler()
        self._cookies = None
        self._skey = None
        self._qq = None
        self.bkn = None
        
    async def login(self, timeout: int = 120):
        try:
            qrsig = await self.qr_handler.generate_qrcode()
            if not qrsig:
                return {"code": -1, "msg": "获取二维码失败"}
                
            cookies = await self.cookie_handler.get_cookies(qrsig)
            if not cookies:
                return {"code": -2, "msg": "登录超时或取消"}
                
            self._cookies = cookies
            self._skey = cookies.get("skey")
            self._qq = cookies.get("uin")
            self.bkn = bkn(cookies.get("skey"))
            
            return {"code": 0, "msg": "登录成功", "cookies": self._cookies, "skey": self._skey, "qq": self._qq, "bkn": self.bkn}
            
        except Exception as e:
            logger.exception("登录过程发生错误")
            return {"code": -999, "msg": str(e)}