import base64
import urllib
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .BasicUtilClass import BaseUtilClass


class HttpSession(BaseUtilClass):
    def __init__(self, logger, endpoint=None, max_retries=3, timeout=5):
        super().__init__(logger)
        self.max_retries = max_retries
        self.timeout = timeout
        self.endpoint = endpoint
        self.session = self.setup_session()

    def setup_session(self):
        session = requests.session()
        session.headers = {}
        retry = Retry(
            total=self.max_retries,
            read=self.max_retries,
            connect=self.max_retries,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def set_http_basic_auth_headers(self, username, token):
        encoding = self.encoding if hasattr(self, 'encoding') else 'utf-8'
        auth_bs64_encode_str = base64.b64encode(f"{username}:{token}".encode(encoding)).decode(encoding)
        auth_header = {"Authorization": "Basic " + auth_bs64_encode_str}
        if hasattr(self.session, 'headers'):
            self.session.headers.update(auth_header)
        else:
            self.session.headers = auth_header

    def request_conn(self, path, method='get', data=None):
        if path.startswith("http://") or path.startswith("https://"):
            requests_path = path
        elif path.startswith("/"):
            requests_path = f'{self.endpoint}{path}'
        else:
            self.logger.warning(f"Un supported path schema {path}")

        requests_params = dict(
            headers=self.session.headers,
            verify=False,
            timeout=self.timeout
        )

        if self.session.headers.get('Content-Type') in ["application/json"]:
            requests_params["json"] = data
        elif self.session.headers.get("Content-Type") in ["application/x-www-form-urlencoded"]:
            requests_params["data"] = urllib.parse.urlencode(data)
        else:
            requests_params["data"] = data
        retries = 1
        while retries < 5:
            try:
                conn = self.session.request(method, requests_path, **requests_params)
                self.logger.debug(f'{method} url {requests_path}')
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout,
                    requests.exceptions.ConnectionError) as Error:
                retries = retries + 1
                self.logger.warning(Error)
                self.logger.warning(f"try connect {retries}th time")
                time.sleep(3)
                conn = None
        return conn

    def read_json(self, path):
        conn = self.request_conn(path)
        return None if conn is None else conn.json()
