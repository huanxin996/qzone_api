from .api import QzoneApi
from .api.api_parms import (
    format_mention,
    UGC_RIGHT_ALL,
    UGC_RIGHT_FRIEND,
    UGC_RIGHT_PART,
    UGC_RIGHT_SELF,
    UGC_RIGHT_EXCLUDE,
)
from .login import QzoneLogin

__all__ = [
    "QzoneApi", "QzoneLogin", "format_mention",
    "UGC_RIGHT_ALL", "UGC_RIGHT_FRIEND", "UGC_RIGHT_PART",
    "UGC_RIGHT_SELF", "UGC_RIGHT_EXCLUDE",
]
__version__ = "1.1.0"
__author__ = "Huan Xin"
__email__ = "mc.xiaolang@foxmail.com"
"""
QQ空间API封装
"""