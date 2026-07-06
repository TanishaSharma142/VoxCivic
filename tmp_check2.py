import http.client
conn = http.client.HTTPConnection('127.0.0.1', 8000, timeout=10)
try:
    conn.request('GET', '/')
    r = conn.getresponse()
    print('status', r.status)
    print('reason', r.reason)
    print(r.read(500).decode('utf-8', errors='replace'))
except Exception as e:
    print('ERR', repr(e))
finally:
    conn.close()
