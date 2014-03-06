# -*- coding: utf-8 -*-

import os

from common import _CUR_PATH
_DEFAULT_LINKS_FILE_PATH = os.path.join(_CUR_PATH, 'links.txt')

from strata import Variable, Layer, LayerSet, ConfigSpec
from strata.layers import CLILayer, KwargLayer, EnvVarLayer

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


_COMMON_LAYERS = [KwargLayer, CLILayer, EnvVarLayer]
_PROD_LAYERSET = LayerSet('prod', _COMMON_LAYERS)
PROD_CONFIGSPEC = ConfigSpec(VAR_LIST, _PROD_LAYERSET)

ProdConfig = PROD_CONFIGSPEC.make_config(name='ProdConfig')

_DEV_LAYERS = _COMMON_LAYERS + [DevDefaultLayer]
DEV_LAYERSET = LayerSet('dev', _DEV_LAYERS)
DEV_CONFIGSPEC = ConfigSpec(VAR_LIST, DEV_LAYERSET)

DevConfig = DEV_CONFIGSPEC.make_config(name='DevConfig')


if __name__ == '__main__':
    import os, sys
    sys.path.append(os.path.expanduser('~/projects/boltons'))
    from boltons.debugutils import pdb_on_signal
    pdb_on_signal()

    #import pdb;pdb.set_trace()
    dev_config = DevConfig()

    from pprint import pprint
    pprint(dev_config)
    pprint(dev_config._pstate.name_value_map)

    ctable = dev_config._config_proc.to_table()
    import pdb;pdb.set_trace()
