# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['edenpdf', 'edenpdf.tools']

package_data = \
{'': ['*'], 'edenpdf': ['samples/*']}

install_requires = \
['requests>=2.22.0,<3.0.0', 'urllib3>=1.25.0,<2.0.0']

setup_kwargs = {
    'name': 'edenpdf',
    'version': '1.0.1',
    'description': 'ilovepdf.com python API library',
    'long_description': "# edenpdf\n\nilovepdf.com python API library, forked from Andrea Bruschi's pylovepdf\n\n## What it does\n\nThis library allows pdf manipulation using the API of http://www.ilovepdf.com. See the Tools section to know what you can do.\n\n### Prerequisites\n\n* [developer account] (https://developer.ilovepdf.com) to get a public key to use the API.\n* [Python >3.6]\n* [Requests] (http://it.python-requests.org/it/latest/)\n\n## Installation (older version)\n\n```\npip install pylovepdf \n```\n\n## Manual installation (up to date) \n\nDownload the latest release.\n```\npython setup.py install\n```\n\n## Getting started\n\nExample files are located inside samples/.\nChange file paths and the public_key parameter with the one you found in your developer account (see prerequisites).\nRun the files and enjoy.\n\n## Tools\nCurrently the following tools are available:\n\n* compress          (Reduce the size of pdf files)\n* imagepdf          (Converts an image to pdf)\n* merge             (Merge multiple pdf into single file)\n* officepdf         (Office document to pdf conversion)\n* pagenumber        (Place numbers on pages)\n* pdfa              (Converts into PDF/A)\n* pdfjpg            (Converts a pdf into jpeg image)\n* protect           (Add password to a pdf)\n* rotate            (Rotates the pages of a file)\n* split             (Split a pdf)\n* unlock            (Remove the password security from the pdf, the coolest feature ever!)\n* validatepdfa      (Checks the conformity of PDF/A format)\n* watermark         (Adds watermark to the file)\n\n## Example Usage (compress tool)\n```python\nfrom pylovepdf.ilovepdf import ILovePdf\n\nilovepdf = ILovePdf('public_key', verify_ssl=True)\ntask = ilovepdf.new_task('compress')\ntask.add_file('pdf_file')\ntask.set_output_folder('output_directory')\ntask.execute()\ntask.download()\ntask.delete_current_task()\n```\n\n## Alternative Example Usage (compress tool)\nA tool can be created directly:\n```python\nfrom pylovepdf.tools.compress import Compress\n\nt = Compress('public_key', verify_ssl=True)\nt.add_file('pdf_file')\nt.set_output_folder('output_directory')\nt.execute()\nt.download()\nt.delete_current_task()\n```\n## Documentation\n\nPlease see https://developer.ilovepdf.com/docs for up-to-date documentation.\n\n",
    'author': 'Andrea Bruschi',
    'author_email': 'moonx2006@gmail.com',
    'url': 'https://github.com/AndyBTuttofare/pylovepdf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.0,<4.0.0',
}


setup(**setup_kwargs)
