#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.backup import create_backup_snapshot


def main():
    result = create_backup_snapshot()
    print("Backup created")
    print(f"File: {result['filename']}")
    print(f"Path: {result['path']}")


if __name__ == "__main__":
    main()
