import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
from tornado.options import options, define, parse_command_line

import django.core.handlers.wsgi


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ninux.settings")
define('port', type=int, default=8080)


def main():
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
    tornado_app = tornado.web.Application([
        ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
    ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port, address='127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()

main()
