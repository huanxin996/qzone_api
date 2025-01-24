import re,json,html
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger
from lxml import etree
from html import unescape

def clean_escaped_html(html_str: str) -> str:
    """清洗转义的HTML字符串"""
    def hex_to_char(match):
        hex_str = match.group(1)
        return chr(int(hex_str, 16))
    html_str = re.sub(r'\\x([0-9a-fA-F]{2})', hex_to_char, html_str)
    html_str = html_str.replace('\\"', '"')
    html_str = html_str.replace('\\/', '/')
    html_str = html_str.replace('\\n', '\n')
    html_str = unescape(html_str)
    html_str = re.sub(r'\s+', ' ', html_str)
    html_str = html_str.strip()
    return html_str

def html_unesape(html_content: str) -> str:
    """HTML反转义"""
    try:
        html_contents = clean_escaped_html(html_content)
        htmls = etree.HTML(html_contents)
        if htmls is None:
            logger.error("HTML解析失败: 返回None")
            return None
        root = htmls.getroottree()
        logger.debug(f"HTML解析成功, 根元素: {root.getroot().tag}")
        logger.debug(f"子元素数量: {len(htmls.getchildren())}")
        return htmls
    except Exception as e:
        logger.error(f"HTML解析异常: {str(e)}")
        return None
def parse_callback_data(content: str) -> Optional[Dict[str, Any]]:
    """解析_preloadCallback回调数据"""
    try:
        callback_pattern = r'_preloadCallback\((.*)\);?$'
        match = re.search(callback_pattern, content, re.DOTALL)
        if not match:
            logger.error("无法匹配callback数据")
            return None
        json_str = match.group(1)
        data = json.loads(json_str)
        if data.get('code') != 0:
            logger.error(f"QQ空间返回错误: {data.get('message', '未知错误')}")
            return None
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        return None
    except Exception as e:
        logger.error(f"回调数据处理失败: {e}")
        return None

def is_repost_feed_html(feed_element) -> Tuple[bool, Optional[Dict]]:
    """从HTML元素判断是否为转发动态"""
    try:
        is_repost = any([
            feed_element.xpath(".//div[contains(@class, 'f-ct')]"),
            feed_element.xpath(".//div[contains(@class, 'f-quote')]"),
            feed_element.xpath(".//div[contains(@class, 'f-info-quote')]")
        ])
        
        if is_repost:
            original_info = {
                'original_author': ''.join(feed_element.xpath(".//div[contains(@class,'f-quote')]//a[@class='f-name']//text()")).strip(),
                'original_content': ''.join(feed_element.xpath(".//div[contains(@class,'f-quote')]//div[@class='f-info']//text()")).strip(),
                'original_time': ''.join(feed_element.xpath(".//div[contains(@class,'f-quote')]//div[contains(@class,'info-detail')]//text()")).strip()
            }
            logger.debug(f"检测到转发动态,原作者: {original_info['original_author']}")
            return True, original_info
        
        return False, None
        
    except Exception as e:
        logger.error(f"判断转发动态失败: {e}")
        return False, None

def parse_message_ids(response_data: Dict) -> List[str]:
    """解析返回数据中的说说ID列表"""
    try:
        if not response_data or 'msglist' not in response_data:
            logger.warning("返回数据中没有说说列表")
            return []
            
        msg_list = response_data['msglist']
        if not msg_list:
            logger.info("说说列表为空")
            return []
            
        tid_list = [msg.get('tid', '') for msg in msg_list if msg.get('tid')]
        logger.info(f"成功获取到 {len(tid_list)} 条说说ID")
        return tid_list
    except Exception as e:
        logger.error(f"解析说说ID列表时发生错误：{e}")

def parse_feeds(content) -> Optional[Dict[str, Any]]:
    """解析好友动态列表数据"""
    html_content = html.unescape(content)
    htmls = html_unesape(html_content)
    
    if htmls is not None:
        feeds = []
        items = htmls.xpath("//li[contains(@class, 'f-single f-s-s')]")
        logger.debug(f"找到动态项: {len(items)}个")
    for item in items:
        try:
            class_attr = item.get('id', '')
            id_match = re.search(r'fct_(\d+)', class_attr)
            feed_id = id_match.group(1) if id_match else ''
            is_repost, original_info = is_repost_feed_html(item)
            feed = {                   
            'id': feed_id,
            'class_id': class_attr,
            'uin': ''.join(item.xpath(".//i[@name='feed_data']/@data-uin")).strip(),
            'origuin': ''.join(item.xpath(".//i[@name='feed_data']/@data-origuin")).strip(),                                                                                                                                                                                                                                                                                                                                       
            'content': ''.join(item.xpath(".//div[contains(@class,'f-info')]//text()")).strip(),
            'time': ''.join(item.xpath(".//div[contains(@class,'info-detail')]//text()")).strip(),
            'tid': ''.join(item.xpath(".//i[@name='feed_data']/@data-tid")).strip(),
            'origtid': ''.join(item.xpath(".//i[@name='feed_data']/@data-origtid")).strip(),
            'abstime': ''.join(item.xpath(".//i[@name='feed_data']/@data-abstime")).strip()
            }
            images = []
            for img in item.xpath(".//div[contains(@class,'f-ct')]//img"):
                image_info = {
                    'url': img.get('src', ''),
                    'desc': img.get('alt', ''),
                    'origin_url': img.get('data-originurl', '')
                }
                if image_info['url']:
                    images.append(image_info)
            if images:
                feed['images'] = images
            if is_repost and original_info:
                feed.update({'original_info': original_info})
            if feed['id'] and feed['id'] != '0':
                feeds.append(feed)
            else:
                logger.error(f"动态无效: {feed.get('content', '')}")
        except Exception as e:
            logger.error(f"解析单条动态失败: {e}")
            continue
    return {"status": "ok", "data": feeds}

def parse_feed_data(data: dict) -> dict:
    """解析指定用户获取到的说说数据"""
    try:
        feeds = []
        for msg in data.get('msglist', []):
            feed = {
                'cur_key': msg.get('tid', ''),
                'uin': msg.get('uin', ''),
                'timestamp': msg.get('created_time', 0),
                'content': '',
                'images': [],
                'repost': None
            }
            if 'pic' in msg:
                for pic in msg['pic']:
                    feed['images'].append({
                        'url': pic.get('url1', ''),
                        'width': pic.get('width', 0),
                        'height': pic.get('height', 0)
                    })
            if 'rt_con' in msg:
                feed['repost'] = {
                    'uni_key': msg.get('rt_tid', ''),
                    'content': msg['rt_con'].get('content', ''),
                    'author': msg.get('rt_uinname', ''),
                    'uin': msg.get('rt_uin', ''),
                    'time': msg.get('rt_createTime', '')
                }
                
            feeds.append(feed)
        return {
            'status': 'ok',
            'total': len(feeds),
            'data': feeds
        }
    except Exception as e:
        logger.error(f"解析说说数据失败: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }