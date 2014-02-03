# -*- coding: utf-8 -*-

import os
import json

from common import _CUR_PATH
_DEFAULT_LINKS_FILE_PATH = os.path.join(_CUR_PATH, 'links.txt')


from strata import Variable, Layer, LayerSet, ConfigSpec, Provider
from strata.layers import CLILayer, KwargLayer, EnvVarLayer
from strata.errors import MissingValue, InvalidValue, NotProvidable

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


class HostURL(Variable):
    name = 'host_url'
    cli_arg_name = 'host_url'
    is_config_kwarg = True


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
            ServerHost, ServerPort, HostURL, SecretKey]


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
        return _DEFAULT_LINKS_FILE_PATH

    def local_hosting_root_path(self):
        return None

    def server_host(self):
        return '0.0.0.0'

    def server_port(self):
        return 5000

    def host_url(self, server_host, server_port):
        return '%s:%s/' % (server_host, server_port)


_COMMON_LAYERS = [KwargLayer, CLILayer, EnvVarLayer,
                  ProjectJSONConfigLayer, UserJSONConfigLayer]
_PROD_LAYERSET = LayerSet('prod', _COMMON_LAYERS)
PROD_CONFIGSPEC = ConfigSpec(VAR_LIST, _PROD_LAYERSET)

ProdConfig = PROD_CONFIGSPEC.make_config(name='ProdConfig')

_DEV_LAYERS = _COMMON_LAYERS + [DevDefaultLayer]
DEV_LAYERSET = LayerSet('dev', _DEV_LAYERS)
DEV_CONFIGSPEC = ConfigSpec(VAR_LIST, DEV_LAYERSET)

DevConfig = DEV_CONFIGSPEC.make_config(name='DevConfig')


if __name__ == '__main__':
    #import pdb;pdb.set_trace()
    dev_config = DevConfig()

    from pprint import pprint
    pprint(dev_config.results)
    import pdb;pdb.set_trace()
