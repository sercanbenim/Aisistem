import io
from wsgiref.util import setup_testing_defaults

import iq_test_site


def call_app(path, method="GET", data=None, cookie=None):
    environ = {}
    setup_testing_defaults(environ)
    if "?" in path:
        environ["PATH_INFO"], environ["QUERY_STRING"] = path.split("?", 1)
    else:
        environ["PATH_INFO"] = path
        environ["QUERY_STRING"] = ""
    environ["REQUEST_METHOD"] = method
    if cookie:
        environ["HTTP_COOKIE"] = cookie
    if data is not None:
        encoded = io.BytesIO(data.encode())
        environ["wsgi.input"] = encoded
        environ["CONTENT_LENGTH"] = str(len(data))
        environ["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
    else:
        environ["wsgi.input"] = io.BytesIO()
        environ["CONTENT_LENGTH"] = "0"

    headers = {}

    def start_response(status, response_headers):
        headers["status"] = status
        for k, v in response_headers:
            headers.setdefault(k, v)

    body = b"".join(iq_test_site.application(environ, start_response))
    return headers, body


def test_iq_flow():
    # get test page
    headers, _ = call_app("/")
    assert headers["status"].startswith("200")
    cookie = headers.get("Set-Cookie")

    # submit answers
    data = "q0=4&q1=blue&q2=15"
    headers, _ = call_app("/submit", method="POST", data=data, cookie=cookie)
    assert headers["status"].startswith("303")
    assert headers["Location"] == "/pay"

    # pay page (first visit)
    headers, body = call_app("/pay", method="GET", cookie=cookie)
    assert headers["status"].startswith("200")

    # simulate payment
    headers, _ = call_app("/pay?simulate=1", method="GET", cookie=cookie)
    assert headers["status"].startswith("303")
    assert headers["Location"] == "/result"

    # view result
    headers, body = call_app("/result", method="GET", cookie=cookie)
    assert headers["status"].startswith("200")
    assert b"Your score is 3" in body
