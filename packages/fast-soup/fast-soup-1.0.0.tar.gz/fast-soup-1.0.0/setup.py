# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_soup']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.3.2,<5.0.0',
 'cssselect>=1.0.1,<2.0.0',
 'lxml>=4.5.0,<5.0.0']

setup_kwargs = {
    'name': 'fast-soup',
    'version': '1.0.0',
    'description': 'BeautifulSoup interface for lxml',
    'long_description': '\nFastSoup \n\n.. image:: https://travis-ci.org/spumer/FastSoup.svg\n    :target: https://travis-ci.org/spumer/FastSoup\n    :alt: Build Status\n\n.. image:: https://coveralls.io/repos/github/spumer/FastSoup/badge.svg\n    :target: https://coveralls.io/github/spumer/FastSoup\n\n=====================================================================================================================================================\n\nBeautifulSoup interface for lxml\n\nKey features\n============\n\n\n* **FAST** search in tree\n* **FAST** serialize to str\n* BeautifulSoup4 interface to interact with object:\n\n  * Search: ``find``\\ , ``find_all``\\ , ``find_next``\\ , ``find_next_sibling``\n  * Text: ``get_text``\\ , ``string``\n  * Tag: ``name``\\ , ``get``\\ , ``clear``\\ , ``__getitem__``\\ , ``__str__``\n\nInstall\n-------\n\n.. code-block:: bash\n\n   pip install fast-soup==1.0.0\n\nHow to use\n----------\n\n.. code-block:: python\n\n   from fast_soup import FastSoup\n\n   content = ...  # read some html content\n   soup = FastSoup(content)\n\n   # interact like BS4 object\n   result = soup.find(\'a\', id=\'my_link\')\n\n   # interact like lxml object\n   el = result.unwrap()\n\nFAQ\n===\n\n**Q:** BS4 already implement lxml parser. Why i should use FastSoup?\n\n**A:** Yes, BS4 implement **parser**\\ , and it\'s just building the tree. All next interactions proceed with "Python speed":\nsearching, serialization.\nFastSoup internally use lxml and guarantee "C speed".\n\n**Q:** How FastSoup speedup works?\n\n**A:** FastSoup just build **xpath** and execute them. For prevent rebuilding LRU cache used.\n\n**Q:** Why you don\'t support whole interface? This will be soon?\n\n**A:** I wrote functions which speed up parsing in my projects. Just create a issue or pull request and i think we find the solution ;)\n\nMiscellaneous\n-------------\n\nYou can got power of BeautifulSoup when wrap your lxml objects, e.g:\n\n.. code-block:: python\n\n   from fast_soup import Tag\n\n   content = ...  # some bytes ready to parse\n   context = lxml.etree.iterparse(\n       io.BytesIO(content),  ...\n   )\n   for event, elem in context:\n       tag = Tag(elem)\n\n       tag_text = tag.get_text()\n       tag_attr = tag[\'attribute\']\n',
    'author': 'spumer',
    'author_email': 'spumer-tm@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
