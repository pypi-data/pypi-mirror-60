# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mountain_project']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'mountain-project',
    'version': '0.1.0',
    'description': 'Python MountainProject API Client',
    'long_description': '[![CircleCI](https://circleci.com/gh/Ben-Hu/mountain_project.svg?style=svg)](https://circleci.com/gh/Ben-Hu/mountain_project) [![codecov](https://codecov.io/gh/Ben-Hu/mountain_project/branch/master/graph/badge.svg)](https://codecov.io/gh/Ben-Hu/mountain_project) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Ben-Hu/mountain_project.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Ben-Hu/mountain_project/context:python) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) ![License](https://img.shields.io/github/license/Ben-Hu/mountain_project) ![Tag](https://img.shields.io/github/v/tag/Ben-Hu/mountain_project)\n\n# MountainProject\nPython MountainProject API Client\n\n## Getting Started\n- Sign up for MountainProject @ `https://www.mountainproject.com`\n- Get your access key for the MountainProject data API @ `https://www.mountainproject.com/data`\n\n```python\nfrom mountain_project import MountainProject\n\nm = MountainProject("access_key")\nuser = m.get_user("test@test.com")\nticks = m.get_ticks("test@test.com")\ntodos = m.get_todos("test@test.com")\nroutes_by_id = m.get_routes(["106034519", "111519266", "106028737"])\nroutes_by_location = m.get_routes_for_lat_lon(49.6867, -123.1350)\n```',
    'author': 'Ben-Hu',
    'author_email': 'benjqh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
