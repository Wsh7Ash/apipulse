import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from apipulse.health import check_tcp, check_http, aggregate
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
def test_tcp_and_aggregate_down():
    closed = check_tcp('127.0.0.1', 1, timeout=0.3)
    assert not closed['ok']
    res = aggregate([closed])
    assert res['status'] == 'down'
def test_http_ok_and_degraded():
    srv = HTTPServer(('127.0.0.1', 0), H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        up = check_http(f'http://127.0.0.1:{port}/', timeout=2)
        assert up['ok']
        res = aggregate([up, closed := check_tcp('127.0.0.1', 1, timeout=0.3)])
        assert res['status'] == 'degraded'
    finally:
        srv.shutdown()
