from textwrap import dedent
from django.core import management
import configuration
import sys,logging
from django.utils import timezone
from models import Executable,Host,Execution
from versioncontrol import UncommittedModificationsError
logger = logging.getLogger(__name__)

def run(argv):
    '''Run the command passed to bilbo and record the command, plus its inputs/outputs'''

    # Split argv into an executable and some remaining arguments
    # This is an ugly, ugly hack
    executable_command = argv[0]
    interpreter = False
    if executable_command in [ 'python','python.exe' ]:
        # Get the first thing that doesnt look like an argument
        for arg in argv[1:]:
            if arg[0] != '-':
                executable_command = arg
                break

    # Get the appropriate host object
    host = Host.get_current_host()

    # Get the appropriate executable object
    logger.debug('Getting object for command %s' % executable_command)
    executable = Executable.get_from_command(executable_command,interpreter)

    # Get the appropriate version object
    logger.debug('Getting version object for executable %s' % executable)
    version = executable.get_version()

    logger.debug('Executable %s version is %s' % (executable,version))

    # Check for uncommitted changes
    logger.debug('Checking if executable %s is under version control' % executable)
    if not executable.check_version_control():
        logger.debug('Executable %s is under version control. Checking for uncommitted changes' % executable)
        print '%s is under version control and the repo has uncommitted changes. Please commit the changes and try again.' % executable.path
        sys.exit(1)

    # Create an execution object
    logger.debug('Getting execution object for executable %s version %s with arguments %s' % (executable,version.name,' '.join(argv)))
    execution = Execution.get_execution(executable,host,version,argv)

    # Run the execution
    execution.run()

    logger.debug(str(execution))

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
