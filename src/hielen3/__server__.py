#!/usr/bin/env python
# coding=utf-8
import logging
import waitress

import hielen3.api.glob as app

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)
logger.debug("logger set to DEBUG")
waitress.serve(
        app.__hug_wsgi__,
        listen="*:80",
        ipv4=True,
        ipv6=False,
        threads = 8,
        channel_timeout = 3600,
        expose_tracebacks = True,
        asyncore_use_poll = True,
        url_prefix='/api/hielen'
        )

