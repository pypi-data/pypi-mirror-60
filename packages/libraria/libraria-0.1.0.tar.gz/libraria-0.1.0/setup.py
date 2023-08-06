# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libraria']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'click>=7.0,<8.0',
 'daiquiri>=2.0.0,<3.0.0',
 'requests>=2.22.0,<3.0.0']

entry_points = \
{'console_scripts': ['libraria = libraria.cli:cli']}

setup_kwargs = {
    'name': 'libraria',
    'version': '0.1.0',
    'description': 'A library for searching libraries for books',
    'long_description': '# Libraria\n\nA python library used for searching libraries for books. Currently, only the San Francisco\nBay Area libraries are supported.\n\n# Upcoming Features\n\n- More comprehensive tests\n- implement support for using [advanced search]("https://smplibrary.bibliocommons.com/search")\n\n### Installing\n\n```\npip3 install libraria\nlibraria \'byzantine empire\'\nS76C2550363,The Culture of the Byzantine Empire,BK,[\'9781508150015\', \'150815001X\', \'9781508150060\', \'1508150060\']\nS76C1793574,The Byzantine Empire,BK,[\'9781410305862\', \'1410305864\']\nS76C1672035,Daily Life in the Byzantine Empire,BK,[\'9780313324376\', \'0313324379\']\nS76C2047443,History of the Byzantine Empire,EBOOK,[]\nS76C1340752,The Byzantine Empire,BK,[\'9780684166520\', \'0684166526\']\nS76C2034317,The End of the Byzantine Empire,EBOOK,[]\nS76C1443729,The Byzantine Empire,BK,[\'9781560063070\', \'1560063076\']\nS76C1718171,The Byzantine Empire,BK,[\'9781590188378\', \'1590188373\']\nS76C2636299,The Byzantine Empire,BK,[\'9781680487800\', \'1680487809\', \'9781680488616\', \'1680488619\']\nS76C1618227,The Byzantine Empire,BK,[\'9780761414957\', \'0761414959\']\n```\n\n\n## Running the tests\n\nTo execute tests, run `poetry run pytest tests`\n\n## License\n\nMIT License\n',
    'author': 'Daniel Cardoza',
    'author_email': 'dan@danielcardoza.com',
    'maintainer': 'Daniel Cardoza',
    'maintainer_email': 'dan@danielcardoza.com',
    'url': 'git@github.com:dang3r/libraria.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
