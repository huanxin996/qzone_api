from .api_base import ApiBase
from .api_zone import ApiZone
from .api_feed import ApiFeed

class QzoneApi(ApiZone, ApiFeed):
    pass

__all__ = ['QzoneApi']