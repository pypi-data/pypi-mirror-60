# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nouns', 'nouns.css', 'nouns.obj', 'nouns.templates']

package_data = \
{'': ['*'], 'nouns': ['builtin_templates/*']}

install_requires = \
['results']

entry_points = \
{'console_scripts': ['nouns = nouns:do_command']}

setup_kwargs = {
    'name': 'nouns',
    'version': '0.1.0',
    'description': 'Data-driven templating',
    'long_description': '# `nouns`: Data-deterministic, structure-driven (very experimental) templating\n\n`nouns` does templating a bit differently - the templating itself is quite primitive, with most of the gruntwork taking place in the preprocessing layer.\n\nThis layer converts all the templating data into a very general form that ensures the data is renderable by the templates no matter the structure of the data.\n\n## Hello world\n\nDo traditional template-and-data templating as follows:\n\n    >>> from nouns import template\n    >>> template(dict(name=\'World\'), \'Hello $name!\')\n    Hello World!\n\nBut the more interesting/intended use is to not explicitly pass in a template. Instead, just pass in the data - let the templating engine itself figure out which templates to use.\n\nThe in-built templates are designed to give you something close to what you probably want.\n\nPass in a table of data, you\'ll get a table back. Pass in a dictionary/mapping, you\'ll get the key/value pairs templated in a table. Pass in a list, you\'ll get each list item templated out.\n\n## Experimental status\n\nThis templating system is an experiment in how to craft the most data-driven templating system, where the output is dependent on the things ("nouns") you pass in.\n\nWe will initially use if for rendering data in notebooks, but it\'s definitely not production-ready for web applications or otherwise rendering untrusted data, without a lot of extra customization and filters set up.\n\nHopefully it will continue to evolve toward production-ready status.',
    'author': 'Robert Lechte',
    'author_email': 'robert.lechte@dpc.vic.gov.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
