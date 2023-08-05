# buba
Multi-environment yaml settings following 12 Factor App methodology.

Inspired by gem [rubyconfig](https://rubygems.org/gems/config).

#### Features:
- simple YAML config files
- config files support inheritance and multiple environments
- access config information via convenient object member notation
- support for multi-level settings (Settings.group.subgroup.setting)
   
#### Install:
```bash
pip install buba
```
    
#### Usage:
Create config directories and files in project root directory:
```bash
.
+-- ...
+-- _config
|   +-- environments
|       +-- development.db.yaml
|       +-- production.db.yaml
|       +-- production.common.yaml
|   +-- db.yaml
|   +-- common.yaml
+-- ...
+-- ...
+-- main.py
```
* files loaded by app env (default - development). 
    * First loaded config/*.yaml files
    * Then loaded config/environment/{APP_ENV}*.yaml files (overrides values, there is option to override/merge list values)
    * Then check all loaded keys for overrides in environment variables (db.host will be mapped to PREFIX__DB__HOST)
    

* app env defined by env ver APP_ENV (there is option to override)
* app env config prefix default value is 'APP_CONFIG' (there is option to override)
* app env config splitter default value is '__' (there is option to override)

```python
from os import environ
from buba import Buba

if __name__ == '__main__':
    config = Buba(env_name='APP_ENV', prefix='CONFIG', splitter='::')
    assert config.app_name == 'my_app'
    assert config.db.host == 'localhost_default'
    assert config.db.user == 'user_development'
    assert config.db.password == 'password_development'

    environ['APP_ENV'] = 'production'
    config.load()

    assert config.app_name == 'my_app'
    assert config.db.host == 'localhost_default'
    assert config.db.user == 'user_production'
    assert config.db.password == 'password_production'

    environ['APP_ENV'] = 'production'
    environ['CONFIG::DB::HOST'] = 'production_host'
    environ['CONFIG::APP_NAME'] = 'production_app_name'
    config.load()

    assert config.app_name == 'production_app_name'
    assert config.db.host == 'production_host'
    assert config.db.user == 'user_production'
    assert config.db.password == 'password_production'

```
