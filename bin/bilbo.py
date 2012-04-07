#!C:\Python27\python.exe
"""
Command-line interface to the Bilbo computational laboratory book management tool.
"""

import sys
from bilbo_core import commands, __version__
from sumatra.versioncontrol.base import VersionControlError

modes = ("init", "configure", "info", "run", "list", "delete", "comment", "tag",
         "repeat", "diff", "upgrade", "sync")

usage = """Usage: bilbo <subcommand> [options] [args]
        
Bilbo version %s 

Available subcommands:  
  """ % __version__ 
usage += "\n  ".join(modes)

if len(sys.argv) < 2:
    print usage
    sys.exit(1)

cmd = sys.argv[1]
try:
    main = getattr(commands, cmd)
except AttributeError:
    print usage
    sys.exit(1)

try:
    main(sys.argv[2:])
except VersionControlError, err:
    print "Error:", err.message
    sys.exit(1)
