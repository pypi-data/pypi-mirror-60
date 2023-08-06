# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notebookquery']

package_data = \
{'': ['*'], 'notebookquery': ['css/custom.css']}

install_requires = \
['nouns', 'results']

setup_kwargs = {
    'name': 'notebookquery',
    'version': '0.1.1',
    'description': 'SQL integration and table display for ipython notebooks',
    'long_description': '# `notebookquery`: SQL integration and table display for IPython notebooks\n\nInstall with `pip`:\n\n```bash\npip install notebookquery\n```\n\nThen just import into a notebook:\n\n```python\nimport notebookquery\n```\n\nFrom there you can choose a database with `%db` at the start of a cell, for instance:\n\n```python\n%db postgresql:///example\n```\n\nThen write a query with `%%sql`:\n\n```python\n%%sql\n\nselect * from example_table;\n```\n\n',
    'author': 'Robert Lechte',
    'author_email': 'robert.lechte@dpc.vic.gov.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
