"""Simple IQ test web app using Python's standard library.

Run ``python iq_test_site.py`` to start a basic HTTP server on port 8000.
Users can take the test for free, but they must "pay" before seeing their
score. Payment is simulated by visiting ``/pay?simulate=1``.
"""

import io
import uuid
from http import cookies
from urllib.parse import parse_qs, urlencode
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults

QUESTIONS = [
    ("What is 2 + 2?", "4"),
    ("What is the color of the sky on a clear day?", "blue"),
    ("What is 5 * 3?", "15"),
]

_sessions = {}

TEST_PAGE = """
<html><body>
<h1>Simple IQ Test</h1>
<form method='post' action='/submit'>
    %s
    <button type='submit'>Submit</button>
</form>
</body></html>
"""

PAY_PAGE = """
<html><body>
<h1>Payment Required</h1>
<p>Please pay a small fee to see your results.</p>
<p><a href='/pay?simulate=1'>Simulate Payment</a></p>
</body></html>
"""

RESULT_PAGE = """
<html><body>
<h1>Your Score</h1>
<p>Your score is %d out of %d.</p>
</body></html>
"""


def _get_session(environ):
    cookie_header = environ.get("HTTP_COOKIE", "")
    c = cookies.SimpleCookie()
    c.load(cookie_header)
    sid_cookie = c.get("sid")
    if sid_cookie:
        sid = sid_cookie.value
    else:
        sid = str(uuid.uuid4())
    session = _sessions.setdefault(sid, {"score": 0, "paid": False})
    headers = [("Set-Cookie", f"sid={sid}; Path=/")]
    return session, headers


def _render_questions():
    parts = []
    for i, (q, _a) in enumerate(QUESTIONS):
        parts.append(f"<p>{q}<br><input name='q{i}'></p>")
    return "".join(parts)


def application(environ, start_response):
    setup_testing_defaults(environ)
    session, cookie_headers = _get_session(environ)
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    query = parse_qs(environ.get("QUERY_STRING", ""))

    if path == "/" and method == "GET":
        body = TEST_PAGE % _render_questions()
        start_response("200 OK", [("Content-Type", "text/html")] + cookie_headers)
        return [body.encode()]

    if path == "/submit" and method == "POST":
        length = int(environ.get("CONTENT_LENGTH", 0) or 0)
        data = environ["wsgi.input"].read(length).decode()
        fields = parse_qs(data)
        score = 0
        for i, (_q, answer) in enumerate(QUESTIONS):
            if fields.get(f"q{i}", [""])[0].strip().lower() == answer.lower():
                score += 1
        session["score"] = score
        session["paid"] = False
        headers = [("Location", "/pay"), *cookie_headers]
        start_response("303 See Other", headers)
        return [b""]

    if path == "/pay" and method == "GET":
        if "simulate" in query:
            session["paid"] = True
            headers = [("Location", "/result"), *cookie_headers]
            start_response("303 See Other", headers)
            return [b""]
        start_response("200 OK", [("Content-Type", "text/html")] + cookie_headers)
        return [PAY_PAGE.encode()]

    if path == "/result" and method == "GET":
        if not session.get("paid"):
            headers = [("Location", "/pay"), *cookie_headers]
            start_response("303 See Other", headers)
            return [b""]
        body = RESULT_PAGE % (session.get("score", 0), len(QUESTIONS))
        start_response("200 OK", [("Content-Type", "text/html")] + cookie_headers)
        return [body.encode()]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]


if __name__ == "__main__":
    with make_server("", 8000, application) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
