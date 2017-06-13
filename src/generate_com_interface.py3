"""Generate a com interface modules

 This module is generate a com interface modules for
 Microsoft Office Object Library and
 Microsoft Excel Object Library

"""

import os
import sys
import subprocess
from win32com.client import makepy

currentPath = os.path.dirname(os.path.realpath(__file__))
mseLib = (currentPath + '\\MSE.py3', 'Microsoft Excel 12.0 Object Library')
msoLib = (currentPath + '\\MSO.py3', 'Microsoft Office 12.0 Object Library')

def generate():
    sys.argv = ['', '-o', mseLib[0], mseLib[1]]
    makepy.main()
    sys.argv = ['', '-o', msoLib[0], msoLib[1]]
    makepy.main()

def clean():
    if os.path.exists(mseLib[0]):
        os.remove(mseLib[0])

    if os.path.exists(msoLib[0]):
        os.remove(msoLib[0])

if __name__ == "__main__":
    clean()
    generate()
