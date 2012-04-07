from django.db import models
from bilbo_core.exceptions import ExecutableError
import os, sys,time,subprocess,shlex,platform
from django.utils import timezone
from bilbo_core import settings

class Host(models.Model):
    '''
    A class for holding information about different platforms
    on which scripts are executed.
    '''

    # Define the database fields
    name = models.CharField(max_length=50)
    desription = models.CharField(max_length=200)
    registered = models.DateTimeField('date registered')
    hostname = models.CharField(max_length=200)

    def __unicode__(self):
        ''' Control how host objects are displayed. '''
        return self.name

    @staticmethod
    def get_current_host():
        '''
        Add the current host to the hosts table if it is not already
        present, then return the host object for the current host
        '''

        # Get the host name
        hostname = platform.node()

        # Use django's get_or_create to create the host if it does not exist
        host, created = Host.objects.get_or_create(hostname=hostname,
                  defaults={'name': hostname,
                            'registered':timezone.now()})

        return host

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
                executable_path = filesystem.find_exe_in_path(command)

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

    @staticmethod
    def unknown():
        ''' Get or create an unknown executable object '''
        
        executable, created = Executable.objects.get_or_create(name='unknown_executable',
                                                               host=Host.get_current_host(),
                  defaults={'registered':timezone.now()})

        return executable

class File(models.Model):
    '''A class for holding the information about files which have been used in or created by executions'''

    # Define the database fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created')
    host = models.ForeignKey(Host)
    path = models.CharField(max_length=255)
    executable = models.ForeignKey('Executable')

    def __unicode__(self):
        return 'File %s on %s' % (self.path,self.host.name)

    @staticmethod
    def get_from_unique_name(host,path):
        ''' Get or create a file object from the host and path '''
        
        # Use django's get_or_create to create the executable if it does not exist
        file_object, created = File.objects.get_or_create(path=path,
                                                          host=host,
                  defaults={'name': os.path.basename(path),
                            'creation_date':timezone.now(),
                            'executable':Executable.unknown()})

        return file_object

    class Meta:
        ''' Django needs this to find our model '''
        app_label = 'bilbo_core'

class FileRelationship(models.Model):
    '''A class for holding the information which relates a file to a particular execution'''

    # Define options for the relationship field

    RELATIONSHIP_CHOICES = (
    ('input', 'input file'),
    ('output', 'output_file')
    )

    # Define the database fields
    file_record = models.ForeignKey(File)
    execution = models.ForeignKey('Execution')
    relationship = models.CharField(max_length=50,
                                          choices=RELATIONSHIP_CHOICES)

    class Meta:
        ''' Django needs this to find our model '''
        app_label = 'bilbo_core'

class Execution(models.Model):
    '''A class for holding the information about a specific run of one executable'''

    # Define the database fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    submission_date = models.DateTimeField('date submitted')
    runtime = models.FloatField()
    host = models.ForeignKey(Host)
    executable = models.ForeignKey(Executable)
    full_command = models.CharField(max_length=255)
    output = models.TextField()
    error = models.TextField()
    return_code = models.IntegerField()
    files = models.ManyToManyField(File, through='FileRelationship')

    def __unicode__(self):
        return 'Execution %s run on %s with executable %s' % (self.name,self.host.name,self.executable.name)

    def get_command(self):
        return shlex.split(self.full_command)

    def get_args(self):
        return self.get_command()[1:]
    
    def run(self):

        # See if the command has any existing files in its arguments
        using_files = filesystem.find_files_in_args(self)

        print 'using files:',using_files

        fs_state = filesystem.get_state()
        
        stdout = subprocess.PIPE

        stderr = subprocess.PIPE

        command = self.get_command()

        start_time = time.clock()

        print 'Running %s with arguments %s' % (self.executable.name,
                                                ' '.join(self.get_args()))
        
        try:
            sp = subprocess.Popen(command, bufsize=-1, stdout=stdout,
                                  stderr=stderr)
        except OSError, ose:
            raise ValueError("Program %s does not seem to exist in your $PATH." % command[0])

        self.return_code = sp.wait()

        self.runtime = time.clock() - start_time

        self.output = sp.stdout.read()

        self.error = sp.stderr.read()

        changed_files = filesystem.get_changed_files(fs_state)

        output_files = changed_files

        input_files = using_files.difference(changed_files)

        print 'output files:\n\n',changed_files

        print 'input files:\n\n',input_files

        

        self.save()

        # If we had any input files, add these to the execution
        # (we have to do this here because the execution must be saved
        # before we can add files to it)
        for used_file in input_files:
            self.with_file(used_file)

        # If we had any output files, add these to the execution
        for output_file in output_files:
            self.produced_file(output_file)

    def with_file(self,used_file):

        FileRelationship.objects.create(execution=self,
                                        file_record=used_file,
                                        relationship='input')

    def produced_file(self,used_file):

        FileRelationship.objects.create(execution=self,
                                        file_record=used_file,
                                        relationship='output')

        used_file.executable = self.executable
        used_file.save()

    @staticmethod
    def get_execution(executable,host,argv):
        return Execution(name = time.strftime('%Y%m%d-%H%M%S:')+executable.name,
                         submission_date = timezone.now(),
                         host = host,
                         executable = executable,
                         full_command = ' '.join(argv))

from bilbo_core import filesystem
