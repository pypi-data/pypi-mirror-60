# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extends']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'extends',
    'version': '0.3.0',
    'description': 'A simple Python library that adds a decorator which helps extend functionality of classes by new methods without inheriting them',
    'long_description': '# extends\nA simple Python library that adds a decorator which helps extend functionality of classes by new methods without inheriting them\n\n# Example\n```python3\nfrom dataclasses import dataclass\nfrom typing import List\nfrom extends import extends\n\n\n@dataclass\nclass Student:\n    name: str\n    marks: List[int]\n\n\n@extends(Student)\ndef avg(self: Student) -> float:\n    return sum(self.marks) / len(self.marks)\n\n```\n',
    'author': 'Arthur Hakimov',
    'author_email': 'verybigfolder@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mefolder/extends',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
