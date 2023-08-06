#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : lison
# @Date    : 2020-02-06 14:35
# @File    : logger.py

import logging
import logging.handlers
import os.path
import datetime
import sys


class Logger:
    def __init__(self):
        self._name = "root"
        self._level = logging.ERROR
        self._filename = 'app.log'
        self._format = None
        self._logger = logging.getLogger(self._name)
        pass

    @property
    def level(self):
        return self._level

    @property
    def filename(self):
        return self._filename

    def init(self, name, level, console=True, filename=None):
        if isinstance(filename, str):
            self._filename = os.path.abspath(filename)

        self._level = getattr(logging, level.upper())
        self._format = logging.Formatter(f"[%(mytime)s][%(levelname)s][{name}] %(myfile)s:%(myline)d => %(message)s")

        self._name = name
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._level)

        if console:
            self._set_consolelog()
        if filename:
            self._set_filelog()

    def _set_consolelog(self):
        handler = logging.StreamHandler()
        handler.setLevel(self._level)
        handler.setFormatter(self._format)
        self._logger.addHandler(handler)
        pass

    def _set_filelog(self):
        dirname = os.path.dirname(self._filename)
        os.makedirs(dirname, exist_ok=True)

        handler = logging.handlers.TimedRotatingFileHandler(
            filename=self._filename,
            when="midnight",
            interval=1,
            backupCount=360,
            encoding="utf8"
        )
        handler.setLevel(self._level)
        handler.setFormatter(self._format)
        self._logger.addHandler(handler)
        pass

    @staticmethod
    def _get_extra(depth=1):
        now = datetime.datetime.now()
        formatted_time = "%s,%03d" % (now.strftime("%Y-%m-%d %H:%M:%S"), now.microsecond)

        frame = sys._getframe(depth)
        filename = os.path.split(frame.f_code.co_filename)[1]
        lineno = frame.f_lineno
        return {
            "myfile": filename,
            "myline": lineno,
            "mytime": formatted_time
        }

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs, extra=self._get_extra(depth=2))

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs, extra=self._get_extra(depth=2))

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs, extra=self._get_extra(depth=2))

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs, extra=self._get_extra(depth=2))


logger = Logger()
