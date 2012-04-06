from django.db import models
from django.utils import timezone
import sys,time,subprocess
from bilbo_core.models import Host,Executable

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

    def __unicode__(self):
        return 'Execution %s run on %s with executable %s' % (self.name,self.host.name,self.executable.name)
    
    def run(self):

        stdout = subprocess.PIPE

        stderr = subprocess.PIPE

        command = sys.argv[2:]

        start_time = time.clock()

        try:
            sp = subprocess.Popen(command, bufsize=-1, stdout=stdout,
                                  stderr=stderr)
        except OSError, ose:
            raise ValueError("Program %s does not seem to exist in your $PATH." % command[0])

        self.return_code = sp.wait()

        self.runtime = time.clock() - start_time

        self.output = sp.stdout.read()

        self.error = sp.stderr.read()

    @staticmethod
    def get_execution(executable,host):
        return Execution(name = time.strftime('%Y%m%d-%H%M%S:')+executable.name,
                         submission_date = timezone.now(),
                         host = host,
                         executable = executable,
                         full_command = ' '.join(sys.argv))
