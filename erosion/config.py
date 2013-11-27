# -*- coding: utf-8 -*-

import common

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


class SecretKey(Variable):
    env_var_name = 'EROSION_KEY'


VAR_LIST = [LinkDatabasePath, LocalHostingRootPath,
            ServerHost, ServerPort, SecretKey]


class DevDefaultLayer(Layer):
    def secret_key(self):
        return 'configmanagementisimportantandhistoricallyhard'


_COMMON_LAYERS = [KwargLayer, CLILayer, EnvVarLayer]
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
