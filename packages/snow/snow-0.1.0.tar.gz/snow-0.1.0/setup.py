# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snow',
 'snow.request',
 'snow.request.core',
 'snow.request.helpers',
 'snow.resource',
 'snow.resource.fields',
 'snow.resource.query']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0', 'marshmallow>=3.2.2,<4.0.0', 'ujson>=1.35,<2.0']

setup_kwargs = {
    'name': 'snow',
    'version': '0.1.0',
    'description': 'Python library for ServiceNow',
    'long_description': 'Snow: Python library for ServiceNow\n---\n\n[![image](https://img.shields.io/github/license/rbw/snow?style=flat-square)](https://raw.githubusercontent.com/rbw/snow/master/LICENSE)\n[![image](https://img.shields.io/pypi/v/snowstorm?style=flat-square)](https://pypi.org/project/snowstorm)\n[![image](https://img.shields.io/travis/rbw/snow?style=flat-square)](https://travis-ci.org/rbw/snow)\n[![image](https://img.shields.io/pypi/pyversions/snow?style=flat-square)](https://pypi.org/project/snowstorm)\n\n\nSnow is a simple and lightweight yet powerful and extensible library for interacting with ServiceNow. It works\nwith modern versions of Python and utilizes [asyncio](https://docs.python.org/3/library/asyncio.html).\n\nDocumentation\n---\n\nThe Snow API reference, examples and more is available in the [documentation](https://python-snow.readthedocs.io/en/latest).\n\nDevelopment status\n---\n\nPre-alpha\n\nAuthor\n------\n\nRobert Wikman \\<rbw@vault13.org\\>\n',
    'author': 'Robert Wikman',
    'author_email': 'rbw@vault13.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rbw/snow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
