from datetime import date, datetime
from uuid import UUID

from simplejson import dumps


def default(obj):
    if isinstance(obj, (date, datetime, UUID)):
        return str(obj)

    try:
        return obj.__json__()
    except:
        raise TypeError('Could not convert object to JSON: {}'.format(obj))


class DefaultJSONPlugin:
    def render(self, info, format=None, fragment=False, template=None):
        if isinstance(info, dict):
            info = {
                k:v for k, v in info.items()
                if not k.startswith('tg_')
            }

        return dumps(info, default=default).encode('utf-8')
