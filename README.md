<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://huanxinbot.com/"><img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_hx-yinying/main/.venv/hx_img.png" width="200" height="200" alt="这里放一张oc饭🤤"></a>
</p>

<div align="center">

# QQ 空间 Api 封装

_✨ 电脑网页版空间API的简洁易用封装 ✨_

</div>

<p align="center">
  <a href="https://github.com/huanxin996/qzone_api/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/huanxin996/qzone_api.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/qzone-api">
    <img src="https://img.shields.io/pypi/v/qzone-api" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
  <a href="https://github.com/huanxin996/qzone_api/issues">
    <img src="https://img.shields.io/github/issues/huanxin996/qzone_api" alt="issues">
  </a>
  <a href="https://github.com/huanxin996/qzone_api/stargazers">
    <img src="https://img.shields.io/github/stars/huanxin996/qzone_api.svg" alt="stars">
  </a>
  <a href="https://github.com/huanxin996/qzone_api/network/members">
    <img src="https://img.shields.io/github/forks/huanxin996/qzone_api.svg" alt="forks">
  </a>
</p>

## 📝 介绍

QZone-API 是一个专注于QQ空间操作的轻量级Python异步API封装库，让你能够像官方一样操作QQ空间，而无需繁琐的请求处理和参数构建。基于网页版QQ空间协议开发，支持二维码登录，操作简单便捷。

## ✨ 特性

- **异步支持**: 基于`aiohttp`实现的全异步API调用
- **完整封装**: 常用QQ空间操作简单几行代码即可实现
- **二维码登录**: 便捷的二维码登录机制，无需手动处理复杂的登录流程
- **丰富功能**: 覆盖绝大部分常用QQ空间操作

## 🔧 安装

```bash
pip install qzone-api
```

## 🛠 功能列表

- ✅ 二维码登录
- ✅ 获取指定QQ的动态
- ✅ 获取好友空间动态
- ✅ 点赞指定动态
- ✅ 发表评论(文本)
- ✅ 发送文本说说
- ✅ 删除指定说说
- ✅ 转发说说

## 📚 快速开始

```python
import asyncio
from qzone_api import QzoneApi, QzoneLogin

async def main():
    # 登录QQ空间
    qzone_login = QzoneLogin()
    login_result = await qzone_login.login()
    
    if login_result["code"] == 0:
        print(f"登录成功! QQ: {login_result['qq']}")
        
        # 获取cookies和g_tk等参数
        cookies = login_result["cookies"]
        cookies_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
        skey = login_result["skey"]
        bkn = login_result["bkn"]
        #:请在这里自行管理你的cookies和g_tk等参数
        #TODO：
        # 模块不会存储登录cookies，请自行管理

        # 实例化API
        qzone = QzoneApi()
        
        # 获取说说列表
        messages = await qzone.get_messages_list(
            target_qq=int(login_result["qq"]),
            g_tk=bkn,
            cookies=cookies_str
        )
        
        if messages:
            print(f"成功获取{len(messages)}条说说")
            
            # 发送一条新说说
            await qzone._send_zone(
                target_qq=int(login_result["qq"]),
                content="Hello QZone-API! 这是通过API发送的说说~",
                cookies=cookies_str,
                g_tk=bkn
            )
            print("发送说说成功!")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🧩 项目结构

- **login/**: 处理QQ空间登录、二维码生成及cookie管理
- **api/**: 封装各种QQ空间API操作接口
  - **api_base.py**: 基础请求方法
  - **api_zone.py**: 空间动态相关API
  - **api_feed.py**: 动态操作相关API
  - **api_parms.py**: API请求参数构建
- **utils/**: 工具函数，包括HTML解析、token生成等

## 🙋 常见问题

### Q: 登录时提示"二维码已失效"怎么办?

A: 二维码有效期较短，请重新执行登录方法获取新的二维码。

### Q: 如何获取其他用户的说说?

A: 使用`get_messages_list`方法，将`target_qq`参数设置为目标用户的QQ号。

### Q: 是否支持发送图片说说?

A: 目前仅支持文本说说，图片说说功能计划在未来版本中支持。

## 📋 贡献指南

欢迎为项目提交PR、Issue或建议!

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 📜 开源协议

本项目使用 MIT 协议，请查看 [LICENSE](https://github.com/huanxin996/qzone_api/blob/main/LICENSE) 文件了解更多信息。

## 🔗 联系方式

有问题? 请[提交Issue](https://github.com/huanxin996/qzone_api/issues)或联系我:

- 邮箱: <mailto:mc.xiaolang@foxmail.com>
- 个人网站: [https://blog.huanxinbot.com/](https://blog.huanxinbot.com/)
