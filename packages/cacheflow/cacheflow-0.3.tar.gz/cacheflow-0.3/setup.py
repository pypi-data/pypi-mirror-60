# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cacheflow', 'cacheflow.cache', 'cacheflow.storage', 'cacheflow.web']

package_data = \
{'': ['*'],
 'cacheflow.web': ['ui/*', 'ui/static/*', 'ui/static/css/*', 'ui/static/js/*']}

install_requires = \
['PyYAML>=5.3,<6.0',
 'cloudpickle>=1.2,<2.0',
 'markdown>=3,<4',
 'requests>=2.22,<3.0',
 'tornado>=6.0,<6.1']

entry_points = \
{'cacheflow': ['builtin_python = cacheflow.python:register',
               'builtins = cacheflow.builtin_components:register'],
 'console_scripts': ['cacheflow = cacheflow.cli:main',
                     'cacheflow-web = cacheflow.web.main:main',
                     'noteflow = cacheflow.literal:main']}

setup_kwargs = {
    'name': 'cacheflow',
    'version': '0.3',
    'description': 'Caching Workflow Engine',
    'long_description': "CacheFlow\n=========\n\nCacheFlow is a caching workflow engine, capable of executing dataflows while\nreusing previous results where appropriate, for efficiency. It is very\nextensible and can be used in many projects.\n\nGoals\n-----\n\n* ☑ Python 3 workflow system\n* ☑ Executes dataflows from JSON or YAML files\n* ☐ `Can also load from SQL database <https://gitlab.com/remram44/cacheflow/issues/4>`__\n* ☐ `Parallel execution <https://gitlab.com/remram44/cacheflow/issues/14>`__\n* ☐ `Streaming/batching <https://gitlab.com/remram44/cacheflow/issues/13>`__\n* ☑ Extensible: can add new components, new storage formats, new caching mechanism, new executors\n* ☐ Pluggable: extensions can be installed from PyPI without forking\n* ☑ Re-usable: can execute workflows by itself, but can also be embedded into applications. Some I plan on developing myself:\n\n  * ☑ `Literate programming app <https://gitlab.com/remram44/cacheflow/issues/2>`__: snippets or components embedded into a markdown file, which are executed on render (similar to Rmarkdown). Results would be cached, making later rendering fast\n  * ☐ Integrate in some of my NYU research projects (VisTrails, Vizier, D3M)\n\n* ☐ `Web-based interface allowing collaborative edition of workflows, with automatic re-execution on change <https://gitlab.com/remram44/cacheflow/issues/11>`__\n\nOther ideas:\n\n* ☐ Use Jupyter kernels as backends to execute code (giving me quick access to all the languages they support)\n* ☐ Isolate script execution (to run untrusted Python/... code, for example with Docker)\n\nNon-goals\n---------\n\n* Make a super-scalable and fast workflow execution engine: I'd rather `make executors based on Spark, Dask, Ray <https://gitlab.com/remram44/cacheflow/issues/14>`__ than try to re-implement those from scratch.\n\nStatus\n------\n\nBasic structures are here, extracted from D3M. Execution works. Very few components available. Working on web interface.\n",
    'author': 'Remi Rampin',
    'author_email': 'remi.rampin@nyu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/remram44/cacheflow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
