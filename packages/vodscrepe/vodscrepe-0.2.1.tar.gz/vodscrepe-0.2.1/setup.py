# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vodscrepe']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.8.2,<5.0.0', 'lxml>=4.4.2,<5.0.0', 'tqdm>=4.41.1,<5.0.0']

setup_kwargs = {
    'name': 'vodscrepe',
    'version': '0.2.1',
    'description': 'https://vods.co/ vod scraper',
    'long_description': '# `vodscrepe`\n\n[![](https://img.shields.io/pypi/v/vodscrepe.svg?style=flat)](https://pypi.org/pypi/vodscrepe/)\n[![](https://img.shields.io/pypi/dw/vodscrepe.svg?style=flat)](https://pypi.org/pypi/vodscrepe/)\n[![](https://img.shields.io/pypi/pyversions/vodscrepe.svg?style=flat)](https://pypi.org/pypi/vodscrepe/)\n[![](https://img.shields.io/pypi/format/vodscrepe.svg?style=flat)](https://pypi.org/pypi/vodscrepe/)\n[![](https://img.shields.io/pypi/l/vodscrepe.svg?style=flat)](https://github.com/dawsonbooth/vodscrepe/blob/master/LICENSE)\n\n# Description\n\nThis PyPI package is best described as a tool for scraping the [vods.co](https://vods.co/) website. Currently, the package only supports Super Smash Bros. Melee vods.\n\n# Installation\n\nWith [Python](https://www.python.org/downloads/) installed, simply run the following command to add the package to your project.\n\n```bash\npip install vodscrepe\n```\n\n# Usage\n\nThe following is an example usage of the package, which is also included in the repo as `example.py`:\n\n```python\nfrom vodscrepe import Scraper\nfrom tqdm import tqdm\n\ns = Scraper(\'melee\', debug=True)\n\npages = range(300)\ntry:\n    for vod in s.scrape(pages, show_progress=True):\n        if vod is not None:\n            tqdm.write(str(vod))\nexcept KeyboardInterrupt:\n    tqdm.write("Scraping terminated.")\n\n```\n\nThis example lists information about the vods from the most recent to page 300 in the following fashion:\n\n```bash\npython example.py > sets.txt\n```\n\nThen, the `sets.txt` file becomes populated with vod information...\n\n```txt\n"[\'2020-01-26\'] Genesis 7 - Zain (Marth) vs Hungrybox (Jigglypuff) - Grand Finals - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Mango (Fox) vs Hungrybox (Jigglypuff) - Losers Finals - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Hax (Fox) vs Hungrybox (Jigglypuff) - Losers Semis - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Mango (Falco) vs Zain (Marth) - Winners Finals - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Fiction (Fox) vs Hungrybox (Jigglypuff) - Losers Quarters - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Hax (Fox) vs Leffen (Fox) - Losers Quarters - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Hungrybox (Jigglypuff) vs Zain (Marth) - Winners Semis - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Leffen (Fox) vs Mango (Falco) - Winners Semis - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Fiction (Fox) vs n0ne (Captain Falcon) - Losers Top 8 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Hax (Fox) vs Shroomed (Sheik) - Losers Top 8 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - n0ne (Captain Falcon) vs aMSa (Sheik) - Losers Round 6 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Fiction (Fox) vs Captain Faceroll (Sheik) - Losers Round 6 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Hax (Fox) vs PewPewU (Marth) - Losers Round 6 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Shroomed (Sheik) vs Swedish Delight (Sheik) - Losers Round 6 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - iBDW (Fox) vs Captain Faceroll (Sheik) - Losers Round 5 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Ryobeat (Peach) vs S2J (Captain Falcon) - Losers Round 4 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Mew2King (Marth) vs ARMY (Ice Climbers) - Losers Round 4 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Trif (Peach) vs Swedish Delight (Sheik) - Losers Round 4 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - SFAT (Fox) vs Panda (FL) (Fox) - Losers Round 3 - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Shroomed (Sheik) vs Zain (Marth) - Winners Quarters - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Mango (Falco) vs aMSa (Sheik) - Winners Quarters - Bo5"\n"[\'2020-01-26\'] Genesis 7 - Fiction (Fox) vs Leffen (Fox) - Winners Quarters - Bo3"\nScraping terminated.\n```\n\n...while the terminal details the progress:\n\n```bash\nAll vods:   0%|                                              | 0/300 [00:07<?, ?pages/s]\nPage 0:  37%|████████████████████                            | 22/60 [00:07<00:12,  3.07vods/s]\n```\n\n# License\n\nThis software is released under the terms of [MIT license](LICENSE).\n',
    'author': 'Dawson Booth',
    'author_email': 'pypi@dawsonbooth.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dawsonbooth/vodscrepe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
