# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['carte', 'carte._vendor', 'carte._vendor.boltons', 'carte.resources']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.3,<2.0.0', 'initable>=0.2.0,<0.3.0', 'scipy>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'carte',
    'version': '0.2.2',
    'description': 'Carte is a flexible, extensible reverse-geocode library.',
    'long_description': '<div align="center">\n  <h1>Carte</h1>\n  <a href=https://github.com/fourpeaksstudios/carte/releases/latest>\n    <img src=https://img.shields.io/github/v/release/fourpeaksstudios/carte?style=flat-square>\n  </a>\n  <a href=https://github.com/fourpeaksstudios/carte/blob/master/LICENSE>\n    <img src=https://img.shields.io/github/license/fourpeaksstudios/carte?style=flat-square>\n  </a>\n  <br>\n  <br>\n  <br>\n</div>\n\n[Carte](https://github.com/fourpeaksstudios/carte) is a flexible, extensible reverse-geocode library implemented in Python.\n\n## Installation\n\n### From [PyPI](https://pypi.org/) via `pip`\n\n[Carte](https://github.com/fourpeaksstudios/carte) is available from PyPI via [pip](https://pypi.org/project/carte/).\n\n```sh\npip install carte\n```\n\n### From source using [`poetry`](https://github.com/sdispater/poetry)\n\n__Note:__ It is recommended to build `carte` in a virtual environment due to dependency version requirements.\n\nFrom the root of the repository, install the necessary dependencies via `poetry`:\n\n```sh\npoetry install\n```\n\nThen, build the wheel:\n\n```sh\npoetry build\n```\n\nFinally, outside of your virtual environment, install the wheel using `pip`:\n\n```sh\npip install dist/carte-<version>-py3-none-any.whl\n```\n\n## Usage\n\nCarte is built using resources which inherit from the `Resource` class. A `Carte` instance is instantiated with a list of the `Resource` types it will query:\n\n```python\nimport carte\n\ncarte_instance = carte.Carte([my_resource_type])\n\nresults = carte_instance.query(List of coordinates as tuples...)\n```\n\nMultiple `Carte` instances may be created, and resources will be shared between them by a backing `ResourceStore`.\n\n### Custom Resources\n\nThe flexibility of Carte lies in the `Resource` class, which queries are passed to sequentially via the `query` method. The results of each resource query are aggregated and passed to the next, allowing the creation of resources that mutate previous resources\' results, such as translating a country\'s ISO 3166-1 identifier code into a full name.\n\nFor examples of `Resource` classes, see the `resources` submodule.\n\nDefining your own `Resource` is as simple as inheriting from the `Resource` superclass, and implementing the `load` and `query` methods.\n\n```python\nfrom carte.resources import resource\n\nclass MyCustomResource(resource.Resource):\n    def load(self):\n        # do stuff...\n\n    def query(self, coordinates, results) -> dict:\n        # do other stuff...\n        return results\n```\n\n## Testing\n\nTo run tests, execute the following from the root of the project:\n\n```sh\npoetry run pytest tests/\n```\n\n## License\n\n[Carte](https://github.com/fourpeaksstudios/carte) is licensed under the [GNU Lesser General Public License](https://github.com/fourpeaksstudios/carte/blob/master/LICENSE).\n\n## Attribution\n\n[Carte](https://github.com/fourpeaksstudios/carte) is inspired by [reverse-geocode](https://bitbucket.org/richardpenman/reverse_geocode).\n',
    'author': 'Payson Wallach',
    'author_email': 'payson@fourpeaksstudios.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
