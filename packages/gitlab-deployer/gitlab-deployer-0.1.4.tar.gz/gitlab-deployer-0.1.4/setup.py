# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['deployer']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0', 'python-gitlab>=1.15,<2.0', 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['deployer = deployer.main:cli']}

setup_kwargs = {
    'name': 'gitlab-deployer',
    'version': '0.1.4',
    'description': 'GitLab Deployer',
    'long_description': '# GitLab deployer\n\n\n## Instalation\n\n```\nNew instalation:\npip install -e git+https://github.com/veryevilzed/gitlab-deployer.git#egg=gitlab-deployer\n\nor\n\npip install -e git+git://github.com/veryevilzed/gitlab-deployer.git#egg=gitlab-deployer\n\n\nUpgrade:\npip install -U -e git+https://github.com/veryevilzed/gitlab-deployer.git#egg=gitlab-deployer\n\nor\n\npip install -U -e git+git://github.com/veryevilzed/gitlab-deployer.git#egg=gitlab-deployer\n\n```\n\n\n\n\n',
    'author': 'Dmitry Vysochin',
    'author_email': 'dmitry.vysochin@gmail.com',
    'url': 'https://github.com/veryevilzed/gitlab-deployer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
