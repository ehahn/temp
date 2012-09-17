#!/usr/bin/env python3

from project.storage import *


def main():
    reader = GrammarReader()
    print(reader.read())

if __name__ == '__main__':
    main()
