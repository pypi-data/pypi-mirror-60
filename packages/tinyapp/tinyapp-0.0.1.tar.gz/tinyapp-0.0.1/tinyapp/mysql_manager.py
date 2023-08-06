#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : lison
# @Date    : 2020-02-06 18:57
# @File    : mysql_manager.py

import typing
import pymysql


class Mysql:
    def __init__(self, host=None, port=3306, user=None, password="",
                 database=None, charset="utf8mb4", autocommit=True, usedict=True):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

        cursorclass = pymysql.cursors.DictCursor if usedict else None

        self._conn = pymysql.connect(
            host=host, port=port, user=user, password=password, database=database,
            charset=charset, autocommit=autocommit, defer_connect=True,
            cursorclass=cursorclass,
            program_name="TINYAPP"
        )

        self._create_default_cursor()

    def __str__(self):
        return "Database[mysql://%s:***@%s:%s/%s]" % (self.user, self.host, self.port, self.database)

    def _create_default_cursor(self):
        self._cursor = self.cursor()

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def user(self):
        return self._user

    @property
    def database(self):
        return self._database

    @property
    def connection(self):
        return self._conn

    def cursor(self, cursor=None) -> pymysql.cursors.Cursor:
        return self._conn.cursor(cursor)

    def ping(self):
        self._conn.ping()

    def close(self):
        self._conn.close()

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchmany(self, size=None):
        return self._cursor.fetchmany(size)

    def fetchall(self):
        return self._cursor.fetchall()

    def execute(self, query, args=None):
        return self._cursor.execute(query, args)

    def executemany(self, query, args=None):
        return self._cursor.executemany(query, args)

    def mogrigy(self, query, args=None):
        return self._cursor.mogrify(query, args)


class MysqlManager:
    def __init__(self):
        self._connections = dict()  # type: typing.Dict[str, Mysql]

    def create(self, name, **kwargs):
        assert name not in self._connections, f"Duplicated connection name: {name}"
        conn = Mysql(**kwargs)
        self._connections[name] = conn
        return conn

    def get(self, name):
        conn = self._connections.get(name)
        assert conn, f"Connection not exists: {name}"
        conn.ping()
        return conn

    def shutdown(self):
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()


mysql_manager = MysqlManager()


def create_mysql(name, **kwargs):
    return mysql_manager.create(name, **kwargs)


def get_mysql(name):
    return mysql_manager.get(name)


def shutdown():
    mysql_manager.shutdown()

