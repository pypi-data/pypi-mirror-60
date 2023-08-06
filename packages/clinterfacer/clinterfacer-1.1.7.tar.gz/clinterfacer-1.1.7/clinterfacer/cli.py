#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""cli.py: This python script implements the CommandLineInterface class."""


# standard library(ies)
import argparse
import importlib as il
import logging
from logging import config
import typing

# 3rd party package(s)
try:
    import importlib_resources as ilr
    import temppathlib as tpl
except ImportError as e:
    pass

# local source(s)
from clinterfacer.parser import Parser

logger = logging.getLogger(__name__)


def setup(name: str, verbose: bool, quiet: bool) -> None:
    try:
        with ilr.path(f'{name}.resources', 'logging.ini') as path:
            config.fileConfig(path)
    except (ImportError, FileNotFoundError) as e:
        content = ilr.read_text('clinterfacer.resources', 'logging.template.ini')
        with tpl.TemporaryDirectory(prefix=name, dont_delete=True) as tmp:
            path = tmp.path / 'logging.ini'
            path.write_text(content.format(package = name))
            config.fileConfig(path)
    logger.debug(f'Loaded logging configuration according to the {path} file.')

class CommandLineInterface(object):

    def __init__(self: object, name: str) -> None:
        self.name = name
        self.parser = Parser(name)
        self.logger = logging.getLogger(__name__)


    def parse(self: object, args: typing.List[str] = None) -> argparse.Namespace:
        return self.parser.parse(args)
                    
        
    def main(self: object, args: typing.List[str] = None) -> int:
        args = self.parse(args)
        self.logger.debug(f'Parser the input arguments as follows: {args}')
        setup(self.name, args.verbose, args.quiet)
        module = f'{self.name}.commands'
        if args.command:
            module += f'.{args.command}'.replace('-', '_')
        module = il.import_module(module)
        self.logger.debug(f'Running the main function of the {module} module ...')
        answer = module.main(args)
        self.logger.debug(f'Exiting with {answer} ...')
        return answer
