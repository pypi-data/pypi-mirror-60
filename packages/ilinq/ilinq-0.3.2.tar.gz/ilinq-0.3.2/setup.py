# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ilinq']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ilinq',
    'version': '0.3.2',
    'description': 'linq library',
    'long_description': "ILinq\n=====\n\n.. image:: https://gitlab.com/yassu/ilinq/badges/master/pipeline.svg\n\nThis project provides the module like linq of C# for Python.\n\nHow To Install\n--------------\n\n::\n\n    $ pip install ilinq\n\nFor developers, we enter\n\n::\n\n    $ pip install pipenv\n    $ pipenv install --dev\n\nFirst Example\n-------------\n\n::\n\n    #!/usr/bin/env python\n    # -*- coding: utf-8 -*-\n\n    from ilinq.ilinq import Linq\n\n\n    def is_prime(n):\n        if n < 2:\n            return False\n\n        for j in range(2, n):\n            if n % j == 0:\n                return False\n\n        return True\n\n\n    if __name__ == '__main__':\n        print(\n            Linq(range(10**4))\n            .last(is_prime))\n        # => 9973\n\nLICENSE\n-------\n\nApache 2.0\n",
    'author': 'yassu',
    'author_email': 'mathyassu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/yassu/ilinq/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
