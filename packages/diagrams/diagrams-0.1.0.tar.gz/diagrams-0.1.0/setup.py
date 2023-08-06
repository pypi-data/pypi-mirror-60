# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['diagrams', 'diagrams.aws', 'diagrams.azure', 'diagrams.base', 'diagrams.gcp']

package_data = \
{'': ['*']}

install_requires = \
['graphviz>=0.13.2,<0.14.0', 'jinja2>=2.10,<3.0']

setup_kwargs = {
    'name': 'diagrams',
    'version': '0.1.0',
    'description': 'draw cloud system architecture diagrams in code',
    'long_description': '<p align="center">\n\t<img src="assets/img/diagrams.png"/>\n</p>\n\n<h1 align="center">Diagrams</h1>\n<p align="center">\n    Diagram as Code\n</p>\n\nDiagrams lets you to draw the cloud system architectures in Python code.\n\nIt was born for prototyping a new system architecture without any design tools. You can also describe or visualize the existing system architecture as well.\n\n> NOTE: It does not control the actual cloud resources like cloudformation or terraform, but just for drawing the system architecutrre.\n\n`Diagram as Code` allows you to track the architecture diagram changes on any version control system (same as source code tracking)\n\nDiagrams currently supports three major cloud providers: `AWS`, `Azure`, `GCP`.\n\n> Let me know if you are using diagram! I\'ll add you in showcase page. (I\'m working on it!) :)\n\n## Getting Started\n\nIt uses [Graphviz](https://www.graphviz.org/) to render the diagram, so you need to [install Graphviz](https://graphviz.gitlab.io/download/) to use **diagrams**. After installing graphviz (or already have it), install the **diagrams**.\n\n```shell\n$ pip install diagrams\n```\n\nYou can start with [quick start](https://diagram.mingrammer.com/docs/installattion/#quick-start). And you can find [guides](https://diagram.mingrammer.com/diagram) for more details. \n\n## Examples\n\n## ContributingF\n\nTo contribute to diagram, check out [CONTRIBUTING](CONTRIBUTING.md).\n\n## License\n\n[MIT](LICENSE.md)',
    'author': 'mingrammer',
    'author_email': 'mingrammer@gmail.com',
    'url': 'https://diagrams.mingrammer.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
