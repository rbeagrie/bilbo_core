from django.db import models
from bilbo_core.exceptions import ExecutableError
import os, sys,time,subprocess,shlex,platform
from django.utils import timezone
from bilbo_core import settings,versioncontrol
debug = settings.getboolean('bilbo','debug')

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

    VERSION_CONTROL_CHOICES = (
    ('git', 'git'),
    ('mercurial', 'mercurial'),
    ('subversion', 'subversion'),
    ('none', 'none')
    )

    # Define the database fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    registered = models.DateTimeField('date registered')
    host = models.ForeignKey(Host)
    path = models.CharField(max_length=200)
    version_control = models.CharField(max_length=50,
                                          choices=VERSION_CONTROL_CHOICES)
    version_command = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s on %s' % (self.name,self.host)

    def get_version_control(self):
        # Check if the executable is under version control
        try:
            working_copy = versioncontrol.get_working_copy(os.path.dirname(self.path))
        except versioncontrol.VersionControlError:
            working_copy = False

        # This is a hack
        if working_copy:
            self.version_control = 'git'
        else:
            self.version_control = 'none'

    def get_version_command(self):

        if str(self.version_command) != '':
            return self.version_command

        if str(self.version_control) == '':
            self.get_version_control()
        
        if str(self.version_control) != 'none':
            self.version_command = self.version_control
        else:
            code,output = self.try_version('--version')
            if code:
                self.version_command = '--version'
            else:
                self.version_command = 'unknown'
            
        self.save()

    def try_version(self,command):
        
        full_command = [self.path,self.version_command]
        stdout = subprocess.PIPE
        stderr = subprocess.STDOUT
        sp = subprocess.Popen(full_command,
                              stdout=stdout,
                              stderr=stderr)
        code = sp.wait()

        output = sp.stdout.read()

        return code,output

    def get_version(self):
        if str(self.version_command) == '':
            self.get_version_command()
        
        if self.version_command in ['none','unknown']:
            return Version.unknown(self)
        elif self.version_command in ['git']:
            output = versioncontrol.get_working_copy(os.path.dirname(self.path)).current_version()
        else:
            code,output = self.try_version(self.version_command)
            
        return Version.get_from_string(self,str(output))

    def check_version_control(self):
        if str(self.version_command) == '':
            self.get_version_command()
            
        if self.version_command in ['git']:
            #This is a little hacky
            working_copy = versioncontrol.get_working_copy(os.path.dirname(self.path))
            return not working_copy.repository._repository.is_dirty(untracked_files=True)
        else:
            return True

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
                  defaults={'registered':timezone.now(),
                            'version_control':'none',
                            'version_command':'none'})

        return executable

class Version(models.Model):
    ''' A class for holding version information '''

    name = models.CharField(max_length=50)
    version = models.CharField(max_length=255)
    executable = models.ForeignKey('Executable')

    def __unicode__(self):
        return "%s version %s" % (self.executable.name,self.version)

    @staticmethod
    def unknown(executable):
        ''' Get or create an unknown version object '''
        
        version, created = Version.objects.get_or_create(name='unknown_version',
                                                         executable=executable,
                                                         version='unknown_version')

        return version

    @staticmethod
    def get_from_string(executable,string):

        version, created = Version.objects.get_or_create(executable=executable,
                                                         version=string,
                                                         defaults={'name':string[-20:]})
        return version

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
        return 'File %s on %s id: %i' % (self.path,self.host.name,self.id)

    @staticmethod
    def get_from_current_host(path):
        ''' Get or create a file object from the current host and path '''
        
        # Use django's get_or_create to create the executable if it does not exist
        file_object, created = File.objects.get_or_create(path=path,
                                                          host=Host.get_current_host(),
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
    version = models.ForeignKey(Version)
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

    def find_files_in_args(self):

        used_files = set()
        cleaned_args = []
        
        # Loop over the arguments and check for existing files
        for arg in self.get_command():
            if os.path.exists(arg):
                
                abs_path = os.path.abspath(arg)
                # If the path exits, get the corresponding File object from the database
                used_file = File.get_from_current_host(abs_path)
                
                # Check that the used file wasn't created by this executable
                if used_file.executable != self.executable:

                    used_files.add(used_file)
                    cleaned_args.append(abs_path)
                else:
                    cleaned_args.append(arg)
            else:
                cleaned_args.append(arg)

        return used_files,cleaned_args
    
    def run(self):

        # See if the command has any existing files in its arguments
        # Prepare a new command with absolute paths to existing files
        existing_files,new_command = self.find_files_in_args()

        # Get a set of files and modification times for the current working directory
        cwd_state = filesystem.get_state(os.getcwd())

        # Generate a new, unique working directory for the sub-process
        base_directory = settings.get('bilbo','temp_dir')
        if base_directory == '':
            base_directory = os.getcwd()
        else:
            base_directory = os.path.abspath(base_directory)
        if not os.path.exists(base_directory):
            print 'The temporary directory specified does not exist'
            sys.exit(1)
        temp_path = filesystem.unique_filename_in(base_directory)
        working_directory = os.path.join(base_directory, temp_path)
        
        os.mkdir(working_directory)

        # Prepare to get the output of our command
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

        # Start counting the CPU time
        start_time = time.clock()

        # Run our command
        print 'Running %s with arguments %s' % (self.executable.name,
                                                ' '.join(new_command[1:]))
        
        try:
            sp = subprocess.Popen(new_command,
                                  bufsize=-1,
                                  stdout=stdout,
                                  stderr=stderr,
                                  cwd = working_directory)
        except ValueError, ose:
            raise ValueError("Program %s does not seem to exist in your $PATH." % new_command[0])

        # Get the return code
        self.return_code = sp.wait()

        # Calculate elapsed cpu time
        self.runtime = time.clock() - start_time

        # Read the process' stdout and stderr
        self.output = sp.stdout.read()
        self.error = sp.stderr.read()

        # Pause in debug mode
        if debug: p = raw_input('Pausing...')

        # Check for new files in the working directory and move them to the current directory
        new_files = filesystem.move_new_files(working_directory)

        # Remove the working directory
        if os.path.isdir(working_directory):
            os.rmdir(working_directory)

        # See if any files in our current directory have changed
        # (these must be output files)
        changed_files = filesystem.get_changed_files(os.getcwd(),cwd_state)
        old_output_files = existing_files.intersection(changed_files)
        output_files = old_output_files.union(new_files)

        # Any files listed in the command arguments but not changed
        # by the process must be input files
        input_files = existing_files.difference(changed_files)

        # Save the execution
        self.save()

        # If we had any input files, add these to the execution
        for used_file in input_files:
            self.with_file(used_file)

        # If we had any output files, add these to the execution
        for output_file in output_files:
            self.produced_file(output_file)

        # Save the execution again
        self.save()

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
    def get_execution(executable,host,version,argv):
        return Execution(name = time.strftime('%Y%m%d-%H%M%S:')+executable.name,
                         submission_date = timezone.now(),
                         host = host,
                         executable = executable,
                         version = version,
                         full_command = ' '.join(argv))

from bilbo_core import filesystem
