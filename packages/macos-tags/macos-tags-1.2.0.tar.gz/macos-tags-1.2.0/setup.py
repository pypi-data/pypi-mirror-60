# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['macos_tags']
install_requires = \
['mdfind>=2019.4.13,<2020.0.0', 'xattr>=0.9.7,<0.10.0']

setup_kwargs = {
    'name': 'macos-tags',
    'version': '1.2.0',
    'description': 'A python libraty for working with macOS tags',
    'long_description': '# `macos-tags`\n\nA python library for working with macOS tags.\n\n## Installation\n\n```bash\npip install macos-tags\n```\n\n## Tutorial & Usage\n\nGet files by tag name:\n\n```python\n>>> import macos_tags\n\n>>> macos_tags.find("design")\n[\'/Users/home/apple.jpg\', \'/Users/home/WEB_POSTERS.png\']\n```\n\nCount files by tag name:\n\n```python\n>>> macos_tags.count("design")\n2\n```\n\nList the tags on the file:\n\n```python\n>>> path = "/path/to/file"\n\n>>> macos_tags.get_all(path)\n[Tag(name=\'design\', color=None), Tag(name=\'python\', color=<Color.GREEN: 2>]\n```\n\nAdd a tag to file:\n\n```python\n>>> macos_tags.add("design", file=path)\n```\n\n> When using `str` objects to define a tag, if a tag does not exist in the system, it will be added without a color label.\n\nAdd a new color tag by using `Tag` data class and `Color` enumeration:\n\n```python\n>>> from macos_tags import Tag, Color\n\n\n>>> tag = Tag(name="python", color=Color.GREEN)\n\n>>> macos_tags.add(tag, file=path)\n```\n\nAdd a new color tag using the `str` object, where the tag name and color number (from 1 to 7) are separated by the literal `\\n`:\n\n```python\n>>> tag = f"python\\n{Color.GREEN}"  # == "python\\n2"\n\n>>> macos_tags.add(tag, file=path)\n```\n\n> If the tag already exists in the system with a different color, the new color will be ignored.\n\nRemove tag from file:\n\n```python\n>>> macos_tags.remove(tag, file=path)\n```\n\nRemove all tags from a file at once:\n\n```python\n>>> macos_tags.remove_all(path)\n```\n\nChange all tags in the file:\n\n```python\n>>> macos_tags.get_all(path)\n[Tag(name=\'design\', color=None), Tag(name=\'python\', color=<Color.GREEN: 2>]\n\n>>> new_tags = [Tag("book"), Tag("programming", Color.BLUE)]\n\n>>> macos_tags.set_all(new_tags, file=path)\n\n>>> macos_tags.get_all(path)\n[Tag(name="book", color=None), Tag("programming", <Color.BLUE: 4>]\n```',
    'author': 'Dima Koskin',
    'author_email': 'dmksknn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dmkskn/macos-tags',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
