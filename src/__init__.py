from exceptions import NoConfigFoundError
import logging,os
from handlers import CachedHandler


__version__ = "0.0.1"

formatter = logging.Formatter(
	'%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
handler = CachedHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)

# We dont want to do any setup here in the toplevel package in case we are unit testing

class SettingsPlaceholder(object):
    def __getattr__(self,name):
        '''
        Raise a not implemented exception if anything tries to interact with the
        settings object before it has been loaded.
        '''
        raise NotImplementedError("The settings have not been loaded yet.")

settings = SettingsPlaceholder()

# settings is replaced with some real settings if bilbo_core.commands is imported
