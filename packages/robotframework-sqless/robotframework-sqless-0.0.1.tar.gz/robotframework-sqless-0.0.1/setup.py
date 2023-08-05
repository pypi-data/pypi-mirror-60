# coding: utf-8
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setupargs = {
    'name': 'robotframework-sqless',
    'description': 'robotframework-sqless is a SQL abstraction library for Robot Framework',

    'license': 'GPLv3',
    'version': '0.0.1',

    'packages': ['SQLess', 'SQLess.adaptors'],
    'package_dir': {'': 'src'},
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',

    'author': 'Christian Kokoska',
    'author_email': 'info@softcreate.de',
    'install_requires': [
        'robotframework>=3.1.2',
        'pyyaml>=5.3',
        'nopea>=0.0.4'
        ,
    ],
}

if __name__ == '__main__':
    setup(**setupargs)
