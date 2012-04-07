"""
Define the base classes for the Sumatra version control abstraction layer.
"""

import os.path


class VersionControlError(Exception):
    pass


class Repository(object):
    
    def __init__(self, url):
        if url == ".":
            url = os.path.abspath(url)
        self.url = url
        
    def __str__(self):
        return "%s at %s" % (self.__class__.__name__, self.url)
    
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.url == other.url
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __getstate__(self):
        """For pickling"""
        return {'url': self.url}

    def __setstate__(self, state):
        """For unpickling"""
        self.__init__(state['url'])

class WorkingCopy(object):
    
    def __eq__(self, other):
        return (self.repository == other.repository) and (self.path == other.path) \
               and (self.current_version() == other.current_version()) #and (self.diff() == other.diff())
            
    def __ne__(self, other):
        return not self.__eq__(other)


