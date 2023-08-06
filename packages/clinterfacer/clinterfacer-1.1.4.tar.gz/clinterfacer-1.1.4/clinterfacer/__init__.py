#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""__init__.py: This script includes all the project's metadata."""


# local source(s)
from .cli import CommandLineInterface as CLI


__author__ = (
    'Adriano Henrique Rossette Leite',
)
__email__ = (
    'adrianohrl@gmail.com',
)
__maintainer__ = (
    'Adriano Henrique Rossette Leite',
)
__copyright__ = ''
__credits__ = []
__license__ = ''
__version__ = '1.1.4' # this information should be altered only by the bumpversion tool
__status__ = 'Development' # should typically be one of 'Prototype', 'Development', 
__description__ = 'This framework aims to simplify the creation of Command-Line Interfaces (CLIs) using python.'
__url__ = 'https://gitlab.com/adrianohrl/cli'
__author__ = ', '.join(__author__)
__email__ = ', '.join(__email__)
__maintainer__ = ', '.join(__maintainer__)
options = [
    'Development',
    'Prototype',
    'Production',
]
if __status__ not in options:
    raise Exception(f'Invalid __status__: {__status__}. It should typically be one of the following: {options}')
