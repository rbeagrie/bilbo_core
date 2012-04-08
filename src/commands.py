from textwrap import dedent
from django.core import management
import bilbo_core
import sys
from django.utils import timezone
from bilbo_core.models import Executable,Host,Execution
from bilbo_core.versioncontrol import UncommittedModificationsError

def run(argv):
    '''Run the command passed to bilbo and record the command, plus its inputs/outputs'''

    # Split argv into an executable and some remaining arguments
    # This is an ugly, ugly hack
    executable_command = argv[0]
    if executable_command in [ 'python','python.exe' ]:
        executable_command = argv[1]

    # Get the appropriate host object
    host = Host.get_current_host()

    # Get the appropriate executable object
    executable = Executable.get_from_command(executable_command)

    # Get the appropriate version object
    version = executable.get_version()

    # Check for uncommitted changes
    if not executable.check_version_control():
        print '%s is under version control and the repo has uncommitted changes. Please commit the changes and try again.' % executable.path
        sys.exit(1)

    # Create an execution object
    execution = Execution.get_execution(executable,host,version,argv)

    # Run the execution
    execution.run()

    print execution

    if execution.return_code != 0:
        raise Exception('Program failed!')

def db(argv):
    '''
    We need to manage our databases with django-admin.py, but we have no settings file. This function
    calls django-admin.py from within bilbo so that django has access to the runtime settings
    '''

    # Django expects the first item in argv to be the name of the script, but we parse this out
    # before handing the remaining arguments to the command. Therefore, we have to put the script
    # name back before handing over to django.
    argv.insert(0,sys.argv[0])
    management.execute_from_command_line(argv)
