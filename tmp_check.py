import requests
urls = ['http://127.0.0.1:8000/', 'http://127.0.0.1:8000/priority-queue']
for u in urls:
    try:
        r = requests.get(u, timeout=5)
        print(u, r.status_code)
        print(r.text)
    except Exception as e:
        print('ERR', u, repr(e))
