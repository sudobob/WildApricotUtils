#!/usr/bin/env python3

"""
Take csv exported from google sheets which specifies disposition of spaceman signoff fields..  

"""

import csv
import sys

with open('/tmp/foo') as csvfile:
    reader = csv.reader(csvfile,delimiter=',',quotechar='"')
    for row in reader:
        (keep,smval,waval,membernum) = row
        if keep == 'keep':
            # for signoffs.py:
            # sys.stdout.write(f'"{smval}" : "{waval}",\n')
            #
            # for pasting into WA Memberfields 
            sys.stdout.write(f'{waval}\n')
