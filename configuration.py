from ConfigParser import SafeConfigParser
from django.conf import settings

class Configuration(SafeConfigParser):
    def __init__(self):

        # Call the parent class' init method
        SafeConfigParser.__init__(self)

        # Attempt to find a project specific configuration file
        config_path = self.find_project_specific_config()

        # If it worked, pass the path to the configuration parser
        if config_path:
            self.get_configuration(open(config_path))

        else:

            # Attempt to find a user specific configuration file
            config_path = self.find_user_specific_config()

        # If it worked, pass the path to the configuration parser
        if config_path:
            self.get_configuration(open(config_path))

        else:
            raise Exception("Couldn't find or create a configuration file")

    def find_project_specific_config(self):
        '''
        Look for a bilbo configuration directory somewhere above or
        inside the current working directory.
        '''

        # This is a hack
        return False

    def find_user_specific_config(self):
        '''
        Look for a bilbo configuration directory in the users home
        directory.
        '''

        # This is a hack
        return 'C:\\Users\\Rob\\.bilbo\\bilbo.conf'

    def get_configuration(self,file_pointer):
        '''Read the configuration file and perform some setup'''

        # Read the config file using the parent class readfp method
        # Using readfp allows us to unit test using IO module
        self.readfp(file_pointer)

        # Set up the django configuration
        self.configure_django()

    def configure_django(self):
        '''Set some django variables based on the config file'''
        
        # Convert all the items from the django section of the config file
        # into a dictionary
        django_config = {}
        for key,value in self.items('django'):
            django_config[key]=value

        # Convert all the items from the django-database section of the
        # config file into a separate dictionary and nest it in the main
        # dictionary.
        django_database = {}
        for key,value in self.items('django-database'):
            django_database[key]=value

        django_config['DATABASES'] = {'default':django_database}

        # Tell django where our model definitions are
        django_config['INSTALLED_APPS'] = ('bilbo_core',)
        
        # Pass the dictionary to the django configuration
        settings.configure(**django_config)

    def optionxform(self,option):
        '''
        Override the option formatter to make options case sensitive
        (we need this for django settings to work).
        '''
        return str(option)
