# -*- coding: UTF-8 -*-
'''
Created on 2020-01-28

@author: daizhaolin
'''

from pip._vendor import pkg_resources
from pip._vendor.packaging.utils import canonicalize_name
from pip._internal.cli.main import main as pip


class piplus(object):
    def __init__(self, arg='pip'):
        if type(arg) is str:
            arg = [arg]

        self.plus = self.canonicalize_name(arg)

        self.installed = {}
        for p in pkg_resources.working_set:
            self.installed[canonicalize_name(p.project_name)] = p

    def __repr__(self):
        return ', '.join(self.plus)

    def canonicalize_name(self, names):
        return [canonicalize_name(name) for name in names]

    def get_requires(self, query, deep=0):
        requires = []
        query_names = self.canonicalize_name(query)
        for dist in [self.installed[pkg] for pkg in query_names if pkg in self.installed]:
            for dep in dist.requires():
                requires.append(dep.project_name)

        if requires and deep != 1:
            for project_name in self.get_requires(requires, deep - 1):
                requires.append(project_name)

        return list(set(requires))

    def requires(self, deep=0):
        return piplus(self.get_requires(self.plus, deep))

    def update(self, cache=True):
        commands = ['install', '--upgrade']

        if not cache:
            commands.append('--no-cache-dir')

        commands.extend(self.plus)

        pip(commands)

        return self
