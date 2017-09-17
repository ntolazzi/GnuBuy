__version__ = '1.0'

import json
from kivy.network.urlrequest import UrlRequest
import time


def reset_lock_on_server(url):
    req = UrlRequest(url + '/reset', timeout=1)
    req.wait()
    time.sleep(0.1)

class ShoppingList:
    def __init__(self, url, debug=False):
        self.items = []
        self.debug = debug
        self.url = url
        self.request_success = True
        self.post_request_parameter = dict(timeout=1, method='POST', req_headers={'Content-Type': 'application/json'},
                                           on_success=self.server_success, on_failure=self.server_error)

    def debug_print(self, msg):
        if self.debug:
            print(msg)

    def get_list_from_server(self):
        self.debug_print('downloading list from server')
        req = UrlRequest(self.url, on_success=self.update_item_list, on_failure=self.server_error, timeout=1)
        req.wait()
        time.sleep(0.1)

    def send_list_to_server(self):
        self.debug_print('updating list on server')
        req = UrlRequest(self.url + '/update', req_body=json.dumps(self.items), **self.post_request_parameter)
        req.wait()
        time.sleep(0.1)

    def lock_and_release_list(self, lock):
        req = UrlRequest(self.url + '/lock', req_body=json.dumps({'Lock': lock}), **self.post_request_parameter)
        req.wait()
        time.sleep(0.1)

    def server_success(self, _, result):
        self.debug_print('########Server Success#########')
        self.debug_print(result)
        self.request_success = True

    def server_error(self, _, result):
        self.debug_print('########Server Error#########')
        self.debug_print(result)
        self.request_success = False

    def update_item_list(self, _, result):
        self.debug_print('Updating local list')
        self.debug_print(result)
        self.items = result
        self.request_success = True

if __name__ == '__main__':
    sl = ShoppingList('http://0.0.0.0:5000/list', debug=True)
    sl.get_list_from_server()
    sl.lock_and_release_list(True)
    sl.send_list_to_server()
    sl.lock_and_release_list(False)
    sl.send_list_to_server()