from argparse import ArgumentParser

from . import source
from . import synchronise


def add_handler(subparsers, module):
    program, module_name = module.__name__.split('.', 1)
    parser = subparsers.add_parser(module_name)
    module.configure(parser)
    parser.set_defaults(handler=module.main)


def main(argv=None):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    add_handler(subparsers, source)
    add_handler(subparsers, synchronise)

    args = parser.parse_args(argv)
    args.handler(args)


if __name__ == "__main__":
    main()
