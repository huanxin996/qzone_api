import base64
from typing import Dict, Any, List, Optional, Union, Sequence
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
    build_edit_message_params,
    build_delcomment_ugc_params,
    build_delreply_ugc_params,
    build_comment_like_params,
    build_add_message_board_params,
    build_del_message_board_params,
    build_blog_add_params,
    build_blog_mod_params,
    build_blog_del_params,
    UGC_RIGHT_ALL,
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
                              g_tk: int, ugc_right: int = UGC_RIGHT_ALL,
                              uins: Optional[Sequence[int]] = None
                              ) -> Optional[Union[Dict[str, Any], str]]:
        """发表文本说说。

        ugc_right 控制可见范围：1 所有人 / 4 QQ好友 / 16 部分好友可见 /
        64 仅自己可见 / 128 部分好友不可见。@某人用 ``build_params.format_mention`` 拼进 content。

        uins 为指定名单，仅在 ugc_right=16（指定这些人可见）或 128（指定这些人不可见）
        时生效，传 QQ 号序列即可，内部会拼成官方的 ``allow_uins`` 逗号分隔字段。
        """
        try:
            params = build_publish_params(target_qq, content, ugc_right=ugc_right, uins=uins)
            return await self._make_post_request(url=f"{self.send_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发送说说失败: {e}")
            return None

    async def edit_message(self, target_qq: int, tid: str, content: str, cookies: str,
                           g_tk: int, ugc_right: int = UGC_RIGHT_ALL,
                           ugcright_id: str = "",
                           uins: Optional[Sequence[int]] = None
                           ) -> Optional[Union[Dict[str, Any], str]]:
        """编辑已发说说（emotion_cgi_update，g_tk 需用 p_skey 计算）。

        tid 为说说 id；ugcright_id 取自说说列表里该条的 ``ugcright_id``（可留空）。
        uins 与 :meth:`publish_message` 一致：ugc_right=16/128 时传指定名单 QQ 序列。
        """
        try:
            params = build_edit_message_params(target_qq, tid, content,
                                               ugc_right=ugc_right, ugcright_id=ugcright_id,
                                               uins=uins)
            return await self._make_post_request(url=f"{self.update_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"编辑说说失败: {e}")
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

    async def like_comment(self, opuin: int, host_qq: int, tid: str, comment_id: int,
                           cookies: str, g_tk: int) -> Optional[Union[Dict[str, Any], str]]:
        """点赞说说下的某条评论（internal_dolike_app）。

        host_qq 为说说主人QQ，tid 为说说 id，comment_id 为评论 id。
        """
        try:
            params = build_comment_like_params(opuin, host_qq, tid, comment_id)
            return await self._make_post_request(url=f"{self.dolike_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"点赞评论失败: {e}")
            return None

    async def delete_comment(self, target_qq: int, uin: int, fid: str, comment_id: int,
                             cookies: str, g_tk: int) -> Optional[Union[Dict[str, Any], str]]:
        """删除说说评论（emotion_cgi_delcomment_ugc，g_tk 用 p_skey 计算）。

        comment_id 为评论 id（说说列表里评论的 ``id`` 或发表评论返回的 ``data['id']``）。
        """
        try:
            params = build_delcomment_ugc_params(target_qq, uin, fid, comment_id)
            return await self._make_post_request(url=f"{self.delcomment_ugc_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除评论失败: {e}")
            return None

    async def delete_reply(self, target_qq: int, uin: int, fid: str, comment_id: int,
                           reply_id: int, cookies: str, g_tk: int
                           ) -> Optional[Union[Dict[str, Any], str]]:
        """删除评论回复（emotion_cgi_delreply_ugc，g_tk 用 p_skey 计算）。"""
        try:
            params = build_delreply_ugc_params(target_qq, uin, fid, comment_id, reply_id)
            return await self._make_post_request(url=f"{self.delreply_ugc_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除回复失败: {e}")
            return None

    async def post_message_board(self, host_qq: int, uin: int, content: str,
                                 cookies: str, g_tk: int
                                 ) -> Optional[Union[Dict[str, Any], str]]:
        """在留言板发表留言（add_msgb，g_tk 用 p_skey 计算）。"""
        try:
            params = build_add_message_board_params(host_qq, uin, content)
            return await self._make_post_request(url=f"{self.msgb_add_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发表留言失败: {e}")
            return None

    async def delete_message_board(self, host_qq: int, msg_id: int, author_uin: int,
                                   cookies: str, g_tk: int
                                   ) -> Optional[Union[Dict[str, Any], str]]:
        """删除留言板留言（del_msgb，g_tk 用 p_skey 计算）。

        msg_id 取自 :meth:`get_message_board` 返回留言的 ``id``，author_uin 为该留言的 ``uin``。
        """
        try:
            params = build_del_message_board_params(host_qq, msg_id, author_uin)
            return await self._make_post_request(url=f"{self.msgb_del_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除留言失败: {e}")
            return None

    async def publish_blog(self, uin: int, title: str, content: str, cookies: str,
                           g_tk: int, right_type: int = 1, category: str = "个人日记"
                           ) -> Optional[Union[Dict[str, Any], str]]:
        """发表日志（add_blog，g_tk 用 p_skey 计算）。

        content 为正文 HTML；right_type 权限：1 公开 / 2 QQ好友 / 3 指定 / 4 仅自己。
        返回结果里含新日志的 ``blogid``。
        """
        try:
            params = build_blog_add_params(uin, title, content, right_type, category)
            return await self._make_post_request(url=f"{self.blog_add_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"发表日志失败: {e}")
            return None

    async def edit_blog(self, uin: int, blog_id: int, title: str, content: str,
                        cookies: str, g_tk: int, right_type: int = 1,
                        category: str = "个人日记") -> Optional[Union[Dict[str, Any], str]]:
        """编辑已发日志（mod_blog，g_tk 用 p_skey 计算）。

        blog_id 取自 :meth:`list_blogs` 返回列表里日志的 ``blogId``。
        """
        try:
            params = build_blog_mod_params(uin, blog_id, title, content, right_type, category)
            return await self._make_post_request(url=f"{self.blog_mod_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"编辑日志失败: {e}")
            return None

    async def delete_blog(self, uin: int, host_qq: int, blog_id: int, cookies: str,
                          g_tk: int) -> Optional[Union[Dict[str, Any], str]]:
        """删除日志（del_blog，g_tk 用 p_skey 计算）。"""
        try:
            params = build_blog_del_params(uin, host_qq, blog_id)
            return await self._make_post_request(url=f"{self.blog_del_url}?&g_tk={g_tk}", data=params, cookies=cookies)
        except Exception as e:
            logger.error(f"删除日志失败: {e}")
            return None

    # ---- 兼容别名（旧版本方法名） ----
    _zanzone = like_feed
    _send_zone = publish_message
    _forward_zone = forward_message
    _del_zone = delete_message
    _send_comments = comment_message
