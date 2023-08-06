# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kalc',
 'kalc.misc',
 'kalc.model',
 'kalc.model.kinds',
 'kalc.model.system',
 'kalc.model.system..ipynb_checkpoints',
 'kalc.policies']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1.2,<6.0.0',
 'Pygments>=2.5,<3.0',
 'jsonpatch>=1.24,<2.0',
 'libkubeselector>=0.0.2,<0.0.3',
 'logzero>=1.5.0,<2.0.0',
 'pandas>=0.25.3,<0.26.0',
 'poodle>=0.2.9,<0.3.0',
 'setuptools>=45.0.0,<46.0.0']

entry_points = \
{'console_scripts': ['kalc-dump = kalc.misc.cluster_dump:run',
                     'kalc-optimize = kalc.misc.cli_optimize:tryrun']}

setup_kwargs = {
    'name': 'kalc',
    'version': '0.1.4',
    'description': 'Kalc - the Kubernetes Calculator core',
    'long_description': '# kalc, the Kubernetes calculator\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![PyPI version](https://badge.fury.io/py/kubectl-val.svg)](https://badge.fury.io/py/kalc) [![Build Status](https://travis-ci.org/criticalhop/kalc.svg?branch=master)](https://travis-ci.org/criticalhop/kalc)\n\n# Overview\n\n`kalc` is application aware Kubernetes rebalancing tool built on pure [AI planning](https://github.com/criticalhop/poodle).\n\n# Quick Start\n\n## Requirements\n\n- Linux x86_64\n- Python 3.7+\n- 6+ GB RAM, decent CPU\n- Up to 20GB of disk space in `/tmp` for generated models\n- `kubectl` installed and connected to cluster\n\n## Installation\n\n    pip install kalc\n    \nIf your Linux host has other versions of Python installed you will recieve an error regarding "Could not find a version that satisfies the requirement kalc (from versions: )No matching distribution found for kalc"... If you recieve this, type the following to install kalc\n    \n    python3.7 -m pip install kalc\n\n## Basic usage\n\n    $ kalc-optimize\n\n`kalc-optimize` will generate `bash` scripts containing `kubectl` commands to get to more optimal states. Have a look at those scripts and execute any one of them, then stop and re-run `kalc-optimize`.\n\n## Autopilot\n\n`kalc` can optimize your cluster in background, gradually increasing reliability by rebalancing and reducing cost by freeing nodes with low utilization. You can run `kalc-optimize` as a cron job, wait for X minutes and then run the most recent generated script file.\n\n# Architecture\n\n- `kalc-optimize` will download current cluster state by executing `kubectl get all` and will start generating `bash` scripts into current folder\n- Each generated `bash` script contains a sequence of `kubectl` commands to get the cluster in a more optimal state: better balanced nodes for availability and OOM/eviction resilience and a more compact packing\n- As `kalc` continues to compute, it will emit more optimal states and bigger bash scripts with kubectl commands\n\n`kalc` aims to take into account current policies, anti-affility, SLO levels and best practices from successful production Kubernetes clusters.\n\n# Project Status\n\n`kalc` is a developer preview and currently supports a subset of Kubernetes resources and behaviour model.\n\nWe invite you to follow [@criticalhop](https://twitter.com/criticalhop) on [Twitter](https://twitter.com/criticalhop) and to chat with the team at `#kalc` on [freenode](https://freenode.net/). If you have any questions or suggestions - feel free to open a [github issue](https://github.com/criticalhop/kalc/issues) or contact andrew@kalc.io directly.\n\nFor enterprise enquiries, use the form on our website: [kalc.io](https://kalc.io) or write us an email at info@kalc.io\n',
    'author': 'CriticalHop Team',
    'author_email': 'info@criticalhop.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
