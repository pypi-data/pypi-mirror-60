
import sys
import argparse

from . import unwrapper
from . import version

VERSION = version.__version__


def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument("filename")
    parser.add_argument('output_path')
    args = parser.parse_args()

    uw = unwrapper.Unwrapper(args.filename, args.output_path)
    uw.apply()
