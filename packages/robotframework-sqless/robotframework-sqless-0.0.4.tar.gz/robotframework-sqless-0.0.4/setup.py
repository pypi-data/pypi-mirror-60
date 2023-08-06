# coding: utf-8
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setupargs = {
    'name': 'robotframework-sqless',
    'description': 'robotframework-sqless is a SQL abstraction library for Robot Framework',
    'version': '0.0.4',

    'license': 'Apache License 2.0',

    'packages': ['SQLess', 'SQLess.adapters'],
    'package_dir': {'': 'src'},
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',

    'author': 'Christian Kokoska',
    'author_email': 'info@softcreate.de',
    'url': 'https://github.com/eternalconcert/robotframework-sqless',
    'keywords': 'robotframework testing test automation http client sql orm postgres postgresql mysql sqlite',
    'platforms': 'any',
    'install_requires': [
        'robotframework>=3.1.2',
        'pyyaml>=5.3',
        'nopea>=0.0.4',
    ],
}

if __name__ == '__main__':
    setup(**setupargs)
