from pathlib import Path
from loguru import logger
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
import requests

class QRCodeHandler:
    def __init__(self):
        self.temp_path = "."
        
    async def generate_qrcode(self):
        url = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=549000912&e=2&l=M&s=3&d=72&v=4&t=0.8692955245720428&daid=5&pt_3rd_aid=0'
        
        try:
            r = requests.get(url)
            qrsig = requests.utils.dict_from_cookiejar(r.cookies).get('qrsig')
            
            qr_path = Path(self.temp_path) / 'QR.png'
            qr_path.write_bytes(r.content)
            
            im = Image.open(qr_path)
            im = im.resize((350, 350))
            logger.info('登录二维码获取成功')
            
            decoded_objects = decode(im)
            for obj in decoded_objects:
                qr = qrcode.QRCode()
                qr.add_data(obj.data.decode('utf-8'))
                qr.print_ascii(invert=True)
                
            return qrsig
            
        except Exception as e:
            logger.error(f"生成二维码失败: {e}")
            return None