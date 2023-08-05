import copy
from glob import glob
from json import dumps
from logging import getLogger, basicConfig, INFO
from os import path, environ, getcwd
from yaml import load, FullLoader

logger = getLogger(__name__)
basicConfig(level=INFO,
            format='%(asctime)s %(module)s:%(lineno)d [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

DEFAULT_ENV = 'APP_ENV'
DEFAULT_ENV_PREFIX = 'APP_CONFIG'
DEFAULT_SPLITTER = '__'


class DotDict(dict):
    """ Dict which allow to access to dict values using dot, e.g. my_dict.key.key1 instead my_dict['key']['key1'] """

    def __getattr__(self, item):
        val = self[item]
        if isinstance(val, dict):
            return DotDict(val)
        else:
            return val


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Buba():
    """ Config class (singleton) """

    __metaclass__ = Singleton

    def __init__(self, **kwargs):
        self._options = kwargs
        self.__config = DotDict()
        self._env_prefix = self._options.get('prefix', DEFAULT_ENV_PREFIX).upper()
        self._env_splitter = self._options.get('splitter', DEFAULT_SPLITTER)
        self._raise_error = self._options.get('raise_error', True)
        self._overwrite_arrays = self._options.get('overwrite_arrays', True)

        self.load()

    def load(self):
        self.__config = DotDict()

        env_name = self._options.get('env_name', DEFAULT_ENV).upper()
        try:
            env_value = environ[env_name]
        except KeyError:
            env_value = 'development'
        logger.info('Config initialized! Environment variable: %s=%s', env_name, env_value)

        config_location = self._options.get('configs_path', path.join(getcwd(), 'config'))
        configs = glob(path.join(config_location, '*.yaml'))

        if configs:
            for cfg_file in sorted(configs):
                self._load_config(cfg_file)
        else:
            logger.error('Cannot find config dir/or config files: %s', path.join(config_location, '*.yaml'))
            exit(1)

        env_configs = glob(path.join(config_location, 'environments', '{}*.yaml'.format(env_value)))
        if env_configs:
            for yaml_file in sorted(env_configs):
                self._load_config(yaml_file)
        else:
            logger.info('"{}*.yaml" configs not found!'.format(env_value))

        if self._options.get('use_env', True):
            self._redefine_variables()

    def __repr__(self):
        return dumps(self.__config, sort_keys=True, indent=2)

    def _load_config(self, config_file):
        """ Load yaml config from file """
        logger.debug('Load config file: %s', config_file)
        with open(config_file) as fp:
            cfg = load(fp, Loader=FullLoader)
            if cfg:
                self._deep_update(self.__config, cfg)

    def _redefine_variables(self):
        """ Search for ENV variables with prefix and add them into config dict """
        for env_name in [key for key in environ.keys() if key.startswith(self._env_prefix)]:
            env_val = environ[env_name]
            logger.debug('Found env variable: %s = %s', env_name, env_val)
            keys = env_name. \
                replace(self._env_prefix, ''). \
                lstrip(self._env_splitter). \
                lower(). \
                split(self._env_splitter)
            keys.reverse()
            self._set_config_value(keys, env_val, self.__config)

    def __getattr__(self, item):
        if self._raise_error:
            return self.__config.__getattr__(item)
        else:
            try:
                return self.__config.__getattr__(item)
            except KeyError:
                logger.warning('Key "{}" not found!' % item)
                return

    def _set_config_value(self, keys, value, cfg=None):
        """ Set config value in config dict """
        logger.debug("Set value '%s' for key: %s", value, keys)
        key = keys.pop()
        if keys:
            self._set_config_value(keys, value, cfg.setdefault(key, {}))
        else:
            cfg[key] = value

    def _deep_update(self, target, src):
        for k, v in src.items():
            if type(v) == list:
                if k not in target or self._overwrite_arrays:
                    target[k] = copy.deepcopy(v)
                else:
                    target[k].extend(v)
            elif type(v) == dict:
                if k not in target:
                    target[k] = copy.deepcopy(v)
                else:
                    self._deep_update(target[k], v)
            elif type(v) == set:
                if k not in target or self._overwrite_arrays:
                    target[k] = v.copy()
                else:
                    target[k].update(v.copy())
            else:
                target[k] = copy.copy(v)
