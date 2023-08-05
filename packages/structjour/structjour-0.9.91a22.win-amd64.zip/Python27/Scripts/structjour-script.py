#!C:\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'structjour==0.9.91a22','console_scripts','structjour'
__requires__ = 'structjour==0.9.91a22'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('structjour==0.9.91a22', 'console_scripts', 'structjour')()
    )
