# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['curlipie']

package_data = \
{'': ['*']}

install_requires = \
['CaseInsensitiveDict>=1.0.0,<2.0.0',
 'first>=2.0.2,<3.0.0',
 'hh>=2.0.0,<3.0.0',
 'multidict>=4.7.4,<5.0.0',
 'orjson>=2.2.0,<3.0.0',
 'typed-argument-parser>=1.4,<2.0',
 'yarl>=1.4.2,<2.0.0']

setup_kwargs = {
    'name': 'curlipie',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Nguyễn Hồng Quân',
    'author_email': 'ng.hong.quan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
