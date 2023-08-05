# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['sumo_simple']
install_requires = \
['python-dateutil>=2.8.1,<3.0.0', 'sumologic-sdk>=0.1.8,<0.2.0']

setup_kwargs = {
    'name': 'sumologic-simple',
    'version': '0.1.0',
    'description': 'A simple interface to run SumoLogic queries',
    'long_description': "# Simple Search API for the SumoLogic Python SDK\n\nInstall requires `pip` >= 19.\n\nUsage:\n\n```py\nfrom sumologic import SumoLogic\nfrom sumo_simple import SumoLogicSimple\nfrom datetime import timedelta\n\nsumo = SumoLogic(MY_ACCESS_ID, MY_ACCESS_KEY)\nsimple = SumoLogicSimple(sumo)\n\nfields, messages, aggregates = simple.search('''\n    _sourceCategory=nginx/prod\n''', startTime=timedelta(minutes=-10)\n)\n\nprint([message for message in messages])\n```\n\nTODO: Publish to PyPI\n",
    'author': 'Jarrad Whitaker',
    'author_email': 'akdor1154@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
