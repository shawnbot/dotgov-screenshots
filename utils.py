"""
Some helpful utility functions.
"""

import sys

def readfile(mode="r"):
    """
    Create a file reader for use with argparse.ArgumentParser() option types.
    The filename "-" is aliased to sys.stdin. An exception will be raised if
    the file doesn't exist.

    > import argparse
    > parser = argparse.ArgumentParser()
    > parser.add_option("--input", dest="input",
    >     type=readfile("r"))
    > args = parser.parse_args(["--input", "-"])
    > args.input == sys.stdin
    True
    """
    def _readfile(filename):
        if filename == "-":
            return sys.stdin
        return open(filename, mode)
    return _readfile

def writefile(mode="w"):
    """
    Create a file writer for use with argparse.ArgumentParser() option types.
    An exception will be raised if the file can't be opened for writing.

    > import argparse
    > parser = argparse.ArgumentParser()
    > parser.add_option("--output", dest="output",
    >     type=writefile("w"))
    > args = parser.parse_args(["--output", "/tmp/blah"])
    > type(args.output) is file
    True
    """
    def _writefile(filename):
        return open(filename, mode)
    return _writefile

