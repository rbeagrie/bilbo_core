from django.db import models
from django.utils import timezone
import platform

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
        
        
    class Meta:
        ''' Django needs this to find our model '''
        app_label = 'bilbo_core'

