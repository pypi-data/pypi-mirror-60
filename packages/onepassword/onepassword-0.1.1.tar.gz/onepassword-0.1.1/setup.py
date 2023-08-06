# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['onepassword']
setup_kwargs = {
    'name': 'onepassword',
    'version': '0.1.1',
    'description': 'Python wrapper for the 1password CLI',
    'long_description': None,
    'author': 'Gabriel Chamon Araujo',
    'author_email': 'gchamon@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lettdigital/onepassword-python',
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
