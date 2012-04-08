'''Global bilbo exception classes'''

class ExecutableError(Exception):
    '''The executable does not exist'''
    pass

class NoConfigFoundError(Exception):
    '''The config file does not exist'''
    pass

class NotADirectoryError(Exception):
    '''The temp directory does not exist'''
    pass
