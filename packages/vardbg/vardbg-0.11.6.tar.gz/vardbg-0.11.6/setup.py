# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vardbg', 'vardbg.output', 'vardbg.output.video_writer']

package_data = \
{'': ['*'], 'vardbg': ['assets/fonts/*']}

install_requires = \
['click>=7.0,<8.0',
 'colorama>=0.4.3,<0.5.0',
 'dictdiffer>=0.8.1,<0.9.0',
 'imageio>=2.6.1,<3.0.0',
 'jsonpickle>=1.2,<2.0',
 'opencv-python>=4.1.2,<5.0.0',
 'pillow>=7.0.0,<8.0.0',
 'pygments>=2.5.2,<3.0.0',
 'sortedcontainers>=2.1.0,<3.0.0',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['vardbg = vardbg.main:main']}

setup_kwargs = {
    'name': 'vardbg',
    'version': '0.11.6',
    'description': 'A simple Python debugger and profiler that generates animated visualizations of program flow.',
    'long_description': "# vardbg\n\n![PyPI version](https://img.shields.io/pypi/v/vardbg)\n\nA simple Python debugger and profiler that generates animated visualizations of program flow. It is meant to help with learning algorithms by allowing you to visualize what the algorithms are doing.\n\n**Python 3.6** or newer is required due to the use of f-strings.\n\nThis project was created during [Google Code-in](https://codein.withgoogle.com/) 2019 for [CCExtractor Development](https://ccextractor.org/).\n\n## Demo\n\n![Insertion Sort Demo](https://user-images.githubusercontent.com/7930239/73331199-ead91e00-4217-11ea-939a-54e230827019.gif)\n\n## Features\n\n- Tracking the history of each variable and its contents\n- Tracking elements within containers (lists, sets, dicts, etc.)\n- Ignoring specific variables\n- Profiling the execution of each line\n- Summarizing all variables and execution times after execution\n- Passing arguments to debugged programs\n- Exporting execution history in JSON format and replaying (including program output)\n- Creating videos that show program flow, execution times, variables (with relationships), and output\n- Writing videos in MP4, GIF, and WebP formats\n\n## Installation\n\nThe latest tagged version can be obtained from PyPI:\n\n```bash\npip install vardbg\n```\n\nAlternatively, one can clone this repository and run it directly after installing dependencies:\n\n```bash\ngit clone https://github.com/CCExtractor/vardbg\ncd vardbg\npython3 -m venv venv\nsource venv/bin/activate\npip install poetry\npoetry install .\n./debug.py\n```\n\nIt can also be installed from the repository:\n\n```bash\npip install .\n```\n\nThe above instructions assume the use of a virtual environment to avoid interfering with the system install of Python.\n\n## Usage\n\nAll of the debugger's subcommands and options are documented in the usage help, which is readily available on the command line.\n\nFor example, this command will debug the function `quick_sort` from the file `sort.py` with the arguments `9 3 5 1` and record the session to a JSON file named `sort1.json`:\n\n```bash\nvardbg run sort.py quick_sort -o qsort.json -a 9 -a 3 -a 5 -a 1\n```\n\nA video can then be generated from the above recording:\n\n```bash\nvardbg replay qsort.json -v sort_vis.mp4\n```\n\nIt is possible to generate videos live while running the debugged program, but this is discouraged because the overhead of video creation inflates execution times greatly and thus ruins profiler results. However, if profiling is not important to you, it is a valid use case.\n\n## Configuration\n\nThe video generator has many options: resolution, speed, fonts, and sizes. These options can be modified using a [TOML](https://learnxinyminutes.com/docs/toml/) config file. The [default config](https://github.com/CCExtractor/vardbg/blob/master/vardbg/output/video_writer/default_config.toml) documents the available options, which can be customized in an minimal overlay config without having to duplicate the entire config. The config can then be used by passing the `-c` argument on the command line.\n\nAn example of a simple overlay is the [config](https://github.com/CCExtractor/vardbg/blob/master/demo_config.toml) used to generate official demo videos for embedding in READMEs. This simple config increases the speed (FPS) slightly and adds an intro screen at the beginning of the video.\n\n## Behavior Control\n\nSpecial comments can be added to lines of code that define variables to control how vardbg handles said variable:\n\n- `# vardbg: ignore` — do not display this variable or track its values\n- `# vardbg: ref lst[i]` — treat variable `i` as the index/key of an element in container `lst` (only shown in videos)\n\n## Contributing\n\nFeel free to contribute to this project! You can add features, fix bugs, or make any other improvements you see fit. We just ask that you follow the [code style guidelines](https://github.com/CCExtractor/vardbg/blob/master/CODE_STYLE.md) to keep the code consistent and coherent. These guidelines can easily be enforced before pushing with the [pre-commit](https://pre-commit.com/) framework, which can install Git pre-commit hooks with the `pre-commit install` command.\n\nOnce your contribution meets the guidelines, [open a pull request](https://github.com/CCExtractor/vardbg/compare) to make things official.\n",
    'author': 'Danny Lin',
    'author_email': 'danny@kdrag0n.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CCExtractor/vardbg',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
