# -*- coding: utf-8 -*-

import os
import json

import common

from strata import Variable, Layer, LayerSet, ConfigSpec, Provider
from strata.layers import CLILayer, KwargLayer, EnvVarLayer
from strata.errors import MissingValue, InvalidValue, NotProvidable
from strata.utils import ArgSpec

"""
Configuration variables:

* Link database file path
* Enable/disable local file hosting
* Local file hosting root path
* Server host
* Server port
* Full host URL
* Secret key (for cookie signing)
"""

"""
Origins:

* Command line arguments
* Environment variables
* Config file
* code/defaults/Config kwargs
"""


class LinkDatabasePath(Variable):
    cli_arg_name = 'db_path'
    is_config_kwarg = True


class LocalHostingRootPath(Variable):
    cli_arg_name = 'local_root'
    is_config_kwarg = True


class ServerHost(Variable):
    cli_arg_name = 'host'
    is_config_kwarg = True


class ServerPort(Variable):
    cli_arg_name = 'port'
    is_config_kwarg = True
    json_config_key = 'port'


class SecretKey(Variable):
    env_var_name = 'EROSION_KEY'


VAR_LIST = [LinkDatabasePath, LocalHostingRootPath,
            ServerHost, ServerPort, SecretKey]


class JSONConfigLayer(Layer):
    _prefix = 'project_'
    _autoprovided = ['project_json_config']
    _prefixed = ['json_config']

    def project_json_config(self):
        fn = './config.json'
        try:
            fh = open(fn)
        except IOError:
            raise MissingValue('json config file does not exist: %r' % fn)
        except ValueError as ve:
            raise InvalidValue('unable to load config file %r: %r' % (fn, ve))
        return json.load(fh)

    @classmethod
    def _get_provider(cls, var):
        try:
            return super(JSONConfigLayer, cls)._get_provider(var)
        except NotProvidable as npe:
            pass
        json_config_key = getattr(var, 'json_config_key', None)
        if not json_config_key:
            raise npe

        prefixed_json_config_name = cls._prefix + 'json_config'

        def _get_json_value(json_config):
            return json_config[json_config_key]

        def _get_json_value_prefixed(**kwargs):
            json_config = kwargs.pop(prefixed_json_config_name)
            if kwargs:
                raise TypeError('unexpected keyword aguments: %r' % kwargs)
            return _get_json_value(json_config=json_config)
        new_argspec = ArgSpec((prefixed_json_config_name,), None, None, ())
        _get_json_value_prefixed._argspec = new_argspec

        return Provider(cls, var.name, _get_json_value_prefixed)


class ProjectJSONConfigLayer(Layer):
    _autoprovided = ['project_json_config']

    def project_json_config(self):
        fn = './config.json'
        try:
            fh = open(fn)
        except IOError:
            raise MissingValue('json config file does not exist: %r' % fn)
        except ValueError as ve:
            raise InvalidValue('unable to load config file %r: %r' % (fn, ve))
        return json.load(fh)

    @classmethod
    def _get_provider(cls, var):
        try:
            return super(ProjectJSONConfigLayer, cls)._get_provider(var)
        except NotProvidable as npe:
            pass
        json_config_key = getattr(var, 'json_config_key', None)
        if not json_config_key:
            raise npe

        def _get_project_json_value(project_json_config):
            return project_json_config[json_config_key]
        return Provider(cls, var.name, _get_project_json_value)


class UserJSONConfigLayer(Layer):
    _autoprovided = ['user_json_config']

    def user_json_config(self):
        try:
            fh = open(os.path.expanduser('~/.erosion_config'))
        except IOError:
            raise MissingValue()
        return json.load(fh)

    @classmethod
    def _get_provider(cls, var):
        try:
            return super(UserJSONConfigLayer, cls)._get_provider(var)
        except NotProvidable as npe:
            pass
        json_config_key = getattr(var, 'json_config_key', None)
        if not json_config_key:
            raise npe

        def _get_user_json_value(user_json_config):
            return user_json_config[json_config_key]
        return Provider(cls, var.name, _get_user_json_value)


class DevDefaultLayer(Layer):
    def secret_key(self):
        return 'configmanagementisimportantandhistoricallyhard'

    def link_database_path(self):
        return './links.json'

    def local_hosting_root_path(self):
        return None

    def server_host(self):
        return '0.0.0.0'

    def server_port(self):
        return 5000


_COMMON_LAYERS = [KwargLayer, CLILayer, EnvVarLayer,
                  JSONConfigLayer, UserJSONConfigLayer]
_PROD_LAYERSET = LayerSet('prod', _COMMON_LAYERS)
PROD_CONFIGSPEC = ConfigSpec(VAR_LIST, _PROD_LAYERSET)

_DEV_LAYERS = _COMMON_LAYERS + [DevDefaultLayer]
DEV_LAYERSET = LayerSet('dev', _DEV_LAYERS)
DEV_CONFIGSPEC = ConfigSpec(VAR_LIST, DEV_LAYERSET)

DevConfig = DEV_CONFIGSPEC.make_config(name='DevConfig')

#import pdb;pdb.set_trace()

dev_config = DevConfig()

from pprint import pprint
pprint(dev_config.results)

"""
Issues
------

- SecretKey should not be showing up as provided by CLILayer
- argparser isn't being provided, meaning _get_parsed_arg can't run
"""
