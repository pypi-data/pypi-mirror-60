import requests
# lines below are to disable ssl warning when verify_ssl is set to False
import urllib3

from edenpdf.response import Response

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Request(object):

    @staticmethod
    def send(method, url, payload, headers=None, files=None, stream=None, verify_ssl=True, proxies=None):

        if method == 'post':
            response = requests.post(url, headers=headers, data=payload, files=files, verify=verify_ssl, stream=stream,
                                     proxies=proxies)
        else:
            response = requests.get(url, headers=headers, data=payload, files=files, verify=verify_ssl, stream=stream,
                                    proxies=proxies)

        return Response(response)
