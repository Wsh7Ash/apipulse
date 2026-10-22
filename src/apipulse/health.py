import socket
import time
import requests

def check_tcp(host, port, timeout=1.0):
    t0 = time.perf_counter()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            ok, err = True, None
        except OSError as e:
            ok, err = False, str(e)
    return {'kind': 'tcp', 'target': f'{host}:{port}', 'ok': ok, 'error': err,
            'ms': round((time.perf_counter() - t0) * 1000, 1)}

def check_http(url, timeout=3.0):
    t0 = time.perf_counter()
    try:
        resp = requests.get(url, timeout=timeout)
        ok = resp.status_code < 500
        err = None if ok else f'status {resp.status_code}'
    except requests.RequestException as e:
        ok, err = False, str(e)
    return {'kind': 'http', 'target': url, 'ok': ok, 'error': err,
            'ms': round((time.perf_counter() - t0) * 1000, 1)}

def aggregate(checks):
    if not checks:
        return {'status': 'unknown', 'dependencies': []}
    status = 'ok' if all(c['ok'] for c in checks) else 'degraded'
    if not any(c['ok'] for c in checks):
        status = 'down'
    return {'status': status, 'dependencies': checks}
