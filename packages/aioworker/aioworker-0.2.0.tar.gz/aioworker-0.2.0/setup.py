# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aioworker']

package_data = \
{'': ['*']}

install_requires = \
['aiotools>=0.8.5,<0.9.0']

setup_kwargs = {
    'name': 'aioworker',
    'version': '0.2.0',
    'description': 'Python async worker',
    'long_description': '## aioworker\n\nA Python worker running over `asyncio`\n\n[![Build Status](https://travis-ci.org/python-streaming/aioworker.svg?branch=master)](https://travis-ci.org/python-streaming/aioworker)\n![python version](https://img.shields.io/badge/python-3.8%2B-yellowgreen)\n[![License](https://img.shields.io/github/license/python-streaming/aioworker.svg)](https://github.com/python-streaming/aioworker/blob/master/LICENSE)\n[![codecov](https://codecov.io/gh/python-streaming/aioworker/branch/master/graph/badge.svg)](https://codecov.io/gh/python-streaming/aioworker)\n\n\n### Requirements\n\npython 3.8+\n\n### Installation\n\n```bash\npip install aioworker\n```\n\n### Usage\n\n```python\nimport asyncio\n\nfrom aioworker import Service, Worker\n\nasync def task_1(loop):\n    while True:\n        print(\'Hello world\')\n        await asyncio.sleep(2)\n\n\nif __name__ == \'__main__\':\n    #  Run the server using 1 worker processes.\n    Worker(tasks=[task_1]).run(workers=1)\n```\n\nor run tasks and the webserver\n\n```python\nimport asyncio\n\nfrom aioworker import Service, Worker\n\n\nasync def sleeping(loop):\n    while True:\n        print(\'Sleeping for 2 seconds...\')\n        await asyncio.sleep(2)\n\n\nasync def on_client_connect(reader, writer):\n    """\n    Read up tp 300 bytes of TCP. This could be parsed usign the HTTP protocol for example\n    """\n    data = await reader.read(300)\n    print(f\'TCP Server data received: {data} \\n\')\n    writer.write(data)\n    await writer.drain()\n    writer.close()\n\n\nif __name__ == \'__main__\':\n    # Run the server using 1 worker processes.\n    Worker(\n        tasks=[sleeping],\n        web_server_config={\n            \'client_connected_cb\': on_client_connect,\n        },\n    )).run(workers=1)\n```\n\n### How to stop the worker\n\n`ctrl+c`\n\n### Default values\n\n| Variable | Default |\n|----------|---------|\n| TCP server host| 0.0.0.0|\n| TPC server port | 8888 |\n\n\n### Examples\n\n1. [Hello world](https://github.com/python-streaming/aioworker/blob/master/examples/hello_world.py)\n2. [TCP Server](https://github.com/python-streaming/aioworker/blob/master/examples/worker_tcp_server.py)\n3. [Kafka Consumer](https://github.com/python-streaming/aioworker/blob/master/examples/worker_kafka_consumer.py)\n\n\n### Development\n\n1. Clone this repo\n2. Run `poetry install`\n3. Test using `./scripts/test`\n4. Lint automatically using `./scripts/lint`\n',
    'author': 'Marcos Schroh',
    'author_email': 'schrohm@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
