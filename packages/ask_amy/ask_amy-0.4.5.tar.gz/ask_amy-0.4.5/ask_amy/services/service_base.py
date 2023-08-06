import urllib.request
from urllib.error import URLError
from urllib.parse import urlencode

import logging
import json

logger = logging.getLogger()

class HTTPRequestsError(Exception):
    """ Exception related to our HTTPRequests Objects"""
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'HTTP Request Error: Code {} Reason {}'.format(self.code, self.msg)


class HTTPRequests(object):

    def _http_call(self, url, params=None, data=None, headers={}, return_type=None):

        if params is not None:
            url += "?" + urlencode(params)

        try:
            if data:
                data = data.encode('utf-8')
            request_url = urllib.request.Request(url,data=data, headers=headers)
            with urllib.request.urlopen(request_url) as response:
                data = response.read()
                encoding = response.info().get_content_charset('utf-8')
                ret_val = data.decode(encoding)

                if return_type == 'json':
                    ret_val = json.loads(ret_val)

        except URLError as error:
            reason =None
            code = None
            error_msg ='Error '
            if hasattr(error, 'reason'):
                reason = error.reason
                error_msg = '{} Reason: {}'.format(error_msg, error.reason)
            if hasattr(error, 'code'):
                code = error.code
                error_msg = '{} Code: {}'.format(error_msg, error.code)
            logger.critical(error_msg)
            raise HTTPRequestsError(code, reason)

        return ret_val



