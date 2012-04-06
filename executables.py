from django.db import models
from bilbo_core.hosts import Host
from bilbo_core.exceptions import ExecutableError
import os, sys
from django.utils import timezone

def find_in_path(command):
    '''
    Loop over the directories in the PATH environment variable looking for the something that matches command.
    '''
    
    found = []
    ext = False
    for path in os.getenv('PATH').split(os.pathsep):
        if os.path.exists(os.path.join(path, command)):
            found += [path]
            
    # If we haven't found it, the file might have a .exe extension omitted by the user
    if not found:
        command += '.exe'
        for path in os.getenv('PATH').split(os.pathsep):
            if os.path.exists(os.path.join(path, command)):
                ext = True
                found += [path]

    # If we still haven't found it, raise an exception
    if not found:
        command = command[:-4]
        raise ExecutableError('"%s" could not be found. Please supply the path to the %s executable.' % (command, command))
    else:
        executable_path = os.path.join(found[0], command)
        print 'Running %s' % executable_path
        if len(found) > 1:
            print 'Multiple versions of %s found, using %s. If you wish to use a different version, please specify it explicitly' % (command,executable_path)
    return executable_path

class Executable(models.Model):
    '''A class for holding the executables run by bilbo'''

    # Define options for the version_controlled field

    VERSION_CONTROLLED_CHOICES = (
    ('git', 'git'),
    ('mercurial', 'mercurial'),
    ('subversion', 'subversion'),
    ('false', 'false')
    )

    # Define the database fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    registered = models.DateTimeField('date registered')
    host = models.ForeignKey(Host)
    path = models.CharField(max_length=200)
    version_controlled = models.CharField(max_length=50,
                                          choices=VERSION_CONTROLLED_CHOICES)
    version_command = models.CharField(max_length=50)

    @staticmethod
    def get_from_command(command,host=False):
        '''
        Add the executable specified by command to the executables
        table if it is not already present, then return the executable
        object.
        '''

        # The executable should only have one record no matter
        # where it is run from in the file tree. Unique executables
        # are therefore distinguished by their absolute path.

        # Check if the command is a path
        if os.path.isfile(command):

            # Check if it is absolute
            if os.path.isabs(command):
                executable_path = command

            # If not, get the absolute path
            else:
                executable_path = os.path.abspath(command)

        # If it isn't a path, we'll have to find it in PATH
        else:
            try:
                executable_path = find_in_path(command)

            # If it doesn't exist in PATH, exit with an error message
            except ExecutableError, err:
                print "Error:", err.message
                sys.exit(1)

        # Set some default values
        default_name,ext = os.path.splitext(os.path.basename(executable_path))

        # If we weren't passed a host object, get one
        if not host:
            host = Host.get_current_host()

        # Use django's get_or_create to create the executable if it does not exist
        executable, created = Executable.objects.get_or_create(path=executable_path,
                  defaults={'name': default_name,
                            'registered':timezone.now(),
                            'host':host})

        return executable

    class Meta:
        ''' Django needs this to find our model '''
        app_label = 'bilbo_core'
