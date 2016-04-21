# coding: utf-8


class CORSMiddleware(object):
    ALLOW_ORIGIN = "*"
    ALLOW_HEADERS = ', '.join([
        'Content-Type',
        'X-AVOSCloud-Application-Id',
        'X-AVOSCloud-Application-Key',
        'X-AVOSCloud-Application-Production',
        'X-AVOSCloud-Client-Version',
        'X-AVOSCloud-Request-sign',
        'X-AVOSCloud-Session-Token',
        'X-AVOSCloud-Super-Key',
        'X-Requested-With',
        'X-Uluru-Application-Id,'
        'X-Uluru-Application-Key',
        'X-Uluru-Application-Production',
        'X-Uluru-Client-Version',
        'X-Uluru-Session-Token',
        'X-LC-Id',
        'X-LC-Key',
        'X-LC-Session',
        'X-LC-Sign',
        'X-LC-Prod',
        'X-LC-UA',
    ])
    ALLOW_METHODS = ', '.join(['PUT', 'GET', 'POST', 'DELETE', 'OPTIONS'])
    MAX_AGE = '86400'

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            start_response('200 OK', [
                ('Access-Control-Allow-Origin', environ.get('HTTP_ORIGIN', self.ALLOW_ORIGIN)),
                ('Access-Control-Allow-Headers', self.ALLOW_HEADERS),
                ('Access-Control-Allow-Methods', self.ALLOW_METHODS),
                ('Access-Control-Max-Age', self.MAX_AGE)
            ])
            return ['']
        else:
            def cors_start_response(status, headers, exc_info=None):
                headers.append(('Access-Control-Allow-Origin', self.ALLOW_ORIGIN))
                headers.append(('Access-Control-Allow-Headers', self.ALLOW_HEADERS))
                headers.append(('Access-Control-Allow-Methods', self.ALLOW_METHODS))
                headers.append(('Access-Control-Max-Age', self.MAX_AGE))
                return start_response(status, headers, exc_info)

            return self.app(environ, cors_start_response)
