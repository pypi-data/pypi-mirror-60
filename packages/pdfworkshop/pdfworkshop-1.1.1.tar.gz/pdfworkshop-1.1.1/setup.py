# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pdfworkshop']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.3,<1.5.0',
 'binpacking>=1.4.1,<1.5.0',
 'click>=7.0,<7.1',
 'edenpdf>=1.0.1,<2.0.0']

entry_points = \
{'console_scripts': ['pdfworkshop = pdfworkshop.cli:start']}

setup_kwargs = {
    'name': 'pdfworkshop',
    'version': '1.1.1',
    'description': 'PDF compressor utility, using iLovePDF API',
    'long_description': '# pdfworkshop\n\nPDF compress tool, using iLovePDF API\n\n## Prerequisites\nThe application is compatible with Windows and Linux based systems.\nPython version 3.6 or above is assumed to be installed, as well as pip package manager utility and setuptools module.\n\n## Installation\n```bash\npip install pdfworkshop\n```\nor\n```bash\npython setup.py install\n```\n\nor\n```bash\npip install -e ~/local_fork_repo_path/\n```\n\n## How to run\n```bash\npdfworkshop -h\n```\n\n## Configuration\n| name       | default     | description                                                      |\n|------------|-------------|------------------------------------------------------------------|\n| input_dir  | ./          | Directory where PDF files will be collected from.                |\n| output_dir | ./output/   | Directory where the compressed PDF files will be stored.         |\n| public_key | ""          | Your public API key.                                                     |\n| suffix     | ""          | The suffix given to compressed files (before the extension).     |\n| recursive  | False       | Boolean indicating if input_dir must be scanned recursively. |\n\nThe public_key value must be defined before using the tool for the first time.\nThe required public key can be obtained by creating a developer account on [iLovePDF](https://developer.ilovepdf.com/).\nAny value can be configured using:\n```bash\npdfworkshop config <config_name> <new_config_value>\n```\n\n## Commands\n- list-config - list configuration values\n- config \\<option\\> \\<value\\> - edit tool configuration values\n- run - compress all PDF files stored in input_dir, storing the result in output_dir\n\n## How to use\nBy default, the PDF files to compress should be on the directory from where the tool will be called.\nAfter using the _run_ command, an _output_ directory will be created, where all compressed\nfiles will be stored.\n\n## Example run\n\nTo exercise some of the available commands, one can try to:\n\n- List the current configuration\n```bash\npdfworkshop list-config\n```\n- Define the API public_key value\n```bash\npdfworkshop config public_key <new_public_key>\n```\n- Run PDF compress tool\n```bash\npdfworkshop run\n```\n\n## License\n\nThis project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.\n',
    'author': 'Eden-Box',
    'author_email': 'dev@edenbox.cf',
    'url': 'https://github.com/eden-box/pdfworkshop',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
