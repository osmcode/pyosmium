"""
Simple examoe that counts the number of changes in downloaded changes.

This example shows how to handle replication services.
"""

import sys
import osmium.replication as osmrep

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python read_changes.py <osmfile> [hours]")
        sys.exit(-1)

    # first get the baseline date where we want to start:
    #  the date of the last change in the given imput file.
    last_change = osmrep.newest_change_from_file(sys.argv[1])

    print(last_change)
