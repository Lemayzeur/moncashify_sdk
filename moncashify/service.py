# Python built-in packages
import sys
import json
import time

if sys.version_info >= (3, 0): # Python 3.X
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    from urllib.error import URLError, HTTPError
    from base64 import encodebytes
else: # Python 2.x
    from urllib2 import Request, urlopen, URLError, HTTPError
    from urllib import urlencode
    from base64 import encodestring as encodebytes

REQUEST_TIMEOUT = 10 # seconds

def post(url, data, headers={}):
    response = ''
    status_code = 0

    # encode body data as bytes
    data = data.encode('utf-8')
    request = Request(url, data=data, headers=headers)

    # record time start of the request
    start = time.time()
    try:
        res = urlopen(request, timeout=REQUEST_TIMEOUT)
        response, status_code = res.read().decode('utf-8'), res.code
    except HTTPError as error:
        response, status_code = error.read().decode('utf-8'), error.code
    except URLError as error:
        request_timeout = time.time() - start >= REQUEST_TIMEOUT

        # If the request took more than or equal to REQUEST_TIMEOUT seconds. Timeout error
        if request_timeout:
            status_code = 408
            error = 'Request timeout'
        else: error = str(error)[1:-2].replace('urlopen error', '')

        response, status_code = json.dumps({'error': error}), status_code
    return response, status_code

def encode_url(query):
    return urlencode(query)

def encode_bytes(byte):
    return encodebytes(byte)

def log(key, msg, level=1):
    print("{}: {}".format(key, msg))

def bug_report(key, msg, level=1):
    print("{}: {}".format(key, msg))