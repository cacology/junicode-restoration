#!c:\python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'fonttools==3.0','console_scripts','pyftmerge'
__requires__ = 'fonttools==3.0'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('fonttools==3.0', 'console_scripts', 'pyftmerge')()
    )