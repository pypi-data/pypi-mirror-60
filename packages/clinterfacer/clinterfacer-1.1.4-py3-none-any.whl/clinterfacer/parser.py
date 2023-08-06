#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""parser.py: This python script implements the CommandLineInterface class."""


# standard library(ies)
import argparse
import importlib
import typing

# 3rd party packages
import pkgutil


class Parser(object):

    def __init__(self: object, name: str) -> None:
        self.package = importlib.import_module(name)


    def get_commands(self: object) -> typing.List[str]:
        module = importlib.import_module(f'{self.package.__name__}.subparsers')
        return [name for _, name, _ in pkgutil.iter_modules(module.__path__)]


    def get_parser(self: object) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=self.package.__name__,
            description=self.package.__description__,
            epilog=f'Visit the project website at {self.package.__url__} for support.',
        )
        self.add_arguments(parser)
        return parser

    
    def add_arguments(self: object, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=f'%(prog)s {self.package.__version__}',
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '-V',
            '--verbose',
            help='Increase the verbosity level.',
            action='store_true',
        )
        group.add_argument(
            '-q',
            '--quiet',
            help='Disable all output text messages.',
            action='store_true',
        )
        module = f'{self.package.__name__}.subparsers'
        module = importlib.import_module(module)
        if hasattr(module, 'add_arguments'):
            module.add_arguments(parser)
        subparsers = parser.add_subparsers(dest='command')
        for command in self.get_commands():            
            module = f'{self.package.__name__}.subparsers.{command}'
            module = importlib.import_module(module)
            module.add_parser(subparsers)


    def parse(self: object, args: typing.List[str] = None) -> argparse.Namespace:
        parser = self.get_parser()
        return parser.parse_args(args)
