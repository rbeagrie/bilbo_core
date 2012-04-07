from django.db import models

class Option(models.Model):
    '''
    A class for holding information about the options accepted
    by excecutables.
    '''

    # Define the database fields
    name = models.CharField(max_length=50)

    # Django needs an inner class to find this model

    class Meta:
        app_label = 'bilbo_core'
