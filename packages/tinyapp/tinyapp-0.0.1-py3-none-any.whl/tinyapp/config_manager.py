#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : lison
# @Date    : 2020-02-06 15:44
# @File    : config_manager.py

import os
import os.path
import json
import typing


class ConfigManager:
    def __init__(self):
        self._configs = dict()  # type: typing.Dict[str, dict]
        pass

    def load(self, dirpath):
        dirpath = os.path.abspath(dirpath)
        files = self._get_json_file(dirpath)
        for file in files:
            full_path = os.path.join(dirpath, file)
            cnf = self._parse_json_file(full_path)
            name = os.path.splitext(file)[0]
            assert name not in self._configs, f"Duplicated file:{full_path}"
            self._configs[name] = cnf
        pass

    def get(self, name, *paths, default=None):
        cnf = self._configs[name]
        for path in paths:
            cnf = cnf.get(path) if isinstance(path, str) else cnf[path]
            if cnf is None:
                break
        return cnf if cnf is not None else default

    @staticmethod
    def _get_json_file(path):
        all_files = os.listdir(path)
        return [file for file in all_files if file.endswith('.json')]

    @staticmethod
    def _parse_json_file(path):
        with open(path, mode='r', encoding='utf8') as fp:
            return json.load(fp)


config_manager = ConfigManager()


def get_config(name, *path, default=None):
    return config_manager.get(name, *path, default=default)


def load_config(dirpath):
    config_manager.load(dirpath)
    pass
