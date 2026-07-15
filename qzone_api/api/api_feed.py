import base64
from typing import Dict, Any, List, Optional, Union
from loguru import logger
from .api_base import ApiBase
from .api_parms import (
    build_like_params,
    build_publish_params,
    build_forward_params,
    build_delete_params,
    build_comment_params,
    build_upload_image_params,
    build_image_richval,
    build_publish_image_params,
    build_comment_ugc_params,
    build_reply_params,
    build_delete_photo_params,
)


class ApiFeed(ApiBase):
    """说说的点赞/发表/转发/删除/评论等操作 API"""

    async def like_feed(self, target_qq: int, g_tk: int, fid: str, cur_key: str,
                        uni_key: str, cookies: str) -> Optional[Union[Dict[str, Any], str]]:
        """点赞指定说说"""
        try:
            params = build_like_params(opuin=target_qq, fid=fid, cur_key=cur_key, uni_key=uni_key)
            return await self._make_post_request(url=f"{self.dolike_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"尝试点赞时失败: {e}")
            return None

    async def publish_message(self, target_qq: int, content: str, cookies: str,
                              g_tk: int) -> Optional[Union[Dict[str, Any], str]]:
        """发表文本说说"""
        try:
            params = build_publish_params(target_qq, content)
            return await self._make_post_request(url=f"{self.send_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发送说说失败: {e}")
            return None

    async def forward_message(self, target_qq: int, opuin: int, tid: str, content: str,
                              cookies: str, g_tk: int) -> Optional[Union[Dict[str, Any], str]]:
        """转发说说"""
        try:
            params = build_forward_params(target_qq, opuin, tid, content)
            return await self._make_post_request(url=f"{self.forward_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"转发说说失败: {e}")
            return None

    async def delete_message(self, target_qq: int, fid: str, cookies: str, g_tk: int,
                             curkey: str, timestamp: int) -> Optional[Union[Dict[str, Any], str]]:
        """删除说说"""
        try:
            params = build_delete_params(target_qq, fid, curkey, timestamp)
            return await self._make_post_request(url=f"{self.dell_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除说说失败: {e}")
            return None

    async def comment_message(self, target_qq: int, uin: int, content: str, cookies: str,
                              g_tk: Union[int, str], fid: str) -> Optional[Union[Dict[str, Any], str]]:
        """发表说说评论"""
        try:
            params = build_comment_params(target_qq, uin, content, fid)
            return await self._make_post_request(url=f"{self.send_comments_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发送评论失败: {e}")
            return None

    async def upload_image(self, target_qq: int, image: Union[str, bytes], skey: str,
                           p_skey: str, cookies: str, g_tk: int
                           ) -> Optional[Union[Dict[str, Any], str]]:
        """上传一张图片到 QQ 空间相册。

        image 可为本地文件路径或图片 bytes；skey/p_skey 取自登录 cookies；
        g_tk 需使用 p_skey 计算（``bkn(cookies['p_skey'])``）。
        返回结果的 ``data`` 字段可直接用于发表图片说说或图文评论。
        """
        try:
            if isinstance(image, str):
                with open(image, "rb") as f:
                    raw = f.read()
            else:
                raw = image
            pic_base64 = base64.b64encode(raw).decode()
            params = build_upload_image_params(target_qq, pic_base64, skey, p_skey, g_tk)
            return await self._make_post_request(url=f"{self.upload_url}?g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"上传图片失败: {e}")
            return None

    async def publish_image_message(self, target_qq: int, images: List[Dict[str, Any]],
                                    cookies: str, g_tk: int, content: str = ""
                                    ) -> Optional[Union[Dict[str, Any], str]]:
        """发表图片/图文说说。

        images 为 :meth:`upload_image` 返回结果里的 ``data`` 字段列表；
        content 为空即纯图片说说，非空即图文混合说说。
        """
        try:
            rich = build_image_richval(images)
            params = build_publish_image_params(target_qq, content, rich["richval"], rich["pic_bo"])
            return await self._make_post_request(url=f"{self.send_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发表图片说说失败: {e}")
            return None

    async def comment_message_with_images(self, target_qq: int, uin: int, content: str,
                                          fid: str, cookies: str, g_tk: int,
                                          images: Optional[List[Dict[str, Any]]] = None
                                          ) -> Optional[Union[Dict[str, Any], str]]:
        """发表评论（支持纯文字与图文混合）。

        走 ``emotion_cgi_addcomment_ugc`` 接口，g_tk 需用 p_skey 计算；
        images 为 :meth:`upload_image` 返回的 ``data`` 列表，为空即纯文字评论。
        返回结果的 ``data['id']`` 为该评论 id，可用于 :meth:`reply_comment`。
        """
        try:
            image_urls = [d["url"] for d in images] if images else None
            params = build_comment_ugc_params(target_qq, uin, fid, content, image_urls)
            return await self._make_post_request(url=f"{self.comment_ugc_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发表评论失败: {e}")
            return None

    async def reply_comment(self, target_qq: int, uin: int, content: str, fid: str,
                            comment_id: int, cookies: str, g_tk: int,
                            images: Optional[List[Dict[str, Any]]] = None
                            ) -> Optional[Union[Dict[str, Any], str]]:
        """回复已有评论。

        走 ``emotion_cgi_addreply_ugc`` 接口，g_tk 需用 p_skey 计算；
        comment_id 为被回复评论的 id（评论返回结果的 ``data['id']``）。
        """
        try:
            image_urls = [d["url"] for d in images] if images else None
            params = build_reply_params(target_qq, uin, fid, comment_id, content, image_urls)
            return await self._make_post_request(url=f"{self.reply_ugc_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"回复评论失败: {e}")
            return None

    async def delete_photo(self, uin: int, album_id: str, lloc: str, sloc: str,
                           cookies: str, g_tk: int, priv: int = 1
                           ) -> Optional[Union[Dict[str, Any], str]]:
        """删除自己相册中的某张图片（只能删当前登录账号名下的图片）。

        album_id 为相册ID，lloc/sloc 为图片定位串（取自 ``list_album_photos`` 返回的
        ``lloc``/``sloc``），priv 为相册权限（取自 ``list_albums`` 返回的 ``rights``）；
        g_tk 用 p_skey 计算。
        """
        try:
            params = build_delete_photo_params(uin, album_id, lloc, sloc, priv)
            return await self._make_post_request(url=f"{self.delete_photo_url}?g_tk={g_tk}",
                                                 data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除相册图片失败: {e}")
            return None

    # ---- 兼容别名（旧版本方法名） ----
    _zanzone = like_feed
    _send_zone = publish_message
    _forward_zone = forward_message
    _del_zone = delete_message
    _send_comments = comment_message
