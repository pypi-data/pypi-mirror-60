# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['conflow', 'conflow.froms']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0', 'typing_extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'conflow',
    'version': '0.0.1',
    'description': 'Python configuration manager.',
    'long_description': "=======\nConflow\n=======\n\n.. image:: https://travis-ci.org/singulared/conflow.svg?branch=master\n    :target: https://travis-ci.org/singulared/conflow\n.. image:: https://codecov.io/gh/singulared/conflow/branch/master/graph/badge.svg\n  :target: https://codecov.io/gh/singulared/conflow\n\nProject in early beta. Work in progress!\n\nConflow organizes layered configurations for Python applications.\nConflow allows you to use default settings and extend or override it\nvia merging settings from different sources:\n- Python dictionaries\n- Files: yaml, json, ini\n- Environment variables\n\nQuickstart\n==========\n\n.. code-block:: bash\n\n  pip install conflow\n\nUsage\n=====\n\n.. code-block:: python\n\n  import os\n  from conflow import Config, from_env\n\n  DEFAULT_SETTINGS = {\n      'db': {\n          'master': {\n              'host': 'localhost',\n              'port': 5432,\n          },\n          'slave': {\n              'host': 'localhost',\n              'port': 5433,\n          }\n      }\n  }\n\n  config = Config().merge(DEFAULT_SETTINGS)\n  assert config.db.master.host() == 'localhost'\n\n  os.environ['APP_DB__MASTER__HOST'] = 'remote_host'\n  env_settings = from_env('APP')\n\n  config = Config().merge(DEFAULT_SETTINGS).merge(env_settings)\n  assert config.db.master.host() == 'remote_host'\n\nMotivation\n==========\nIf you are tired of making local, test, stage and production profiles in each project, then Conflow is for you.\nConflow allows you to fetch and merge configs from different places - yaml files, environment variables etc.\n",
    'author': 'Belousow Makc',
    'author_email': 'lib.bmw@gmail.com',
    'url': 'https://github.com/singulared/conflow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
