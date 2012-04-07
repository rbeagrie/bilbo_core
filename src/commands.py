from textwrap import dedent
from django.core import management
import bilbo_core
import sys
from django.utils import timezone
from bilbo_core.models import Executable,Host,Execution

def run(argv):
    '''Run the command passed to bilbo and record the command, plus its inputs/outputs'''

    # Split argv into an executable and some remaining arguments
    executable_command = argv[0]
    arguments = argv[1:]

    # Get the appropriate host object
    host = Host.get_current_host()

    # Get the appropriate executable object
    executable = Executable.get_from_command(executable_command)

    # Create an execution object
    execution = Execution.get_execution(executable,host,argv)

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
