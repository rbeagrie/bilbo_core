import os

def find_files_in_args(execution):

    used_files = []

    # Loop over the arguments and check for existing files
    for arg in execution.get_args():
        if os.path.exists(arg):
            
            abs_path = os.path.abspath(arg)
            # If the path exits, get the corresponding File object from the database
            used_file = File.get_from_unique_name(execution.host,abs_path)
            
            # Check that the used file wasn't created by this executable
            if used_file.executable != execution.executable:

                used_files.append(used_file)

    return used_files
            
def find_in_path(command):
    '''
    Loop over the directories in the PATH environment variable looking for the something that matches command.
    '''
    
    found = []
    for path in os.getenv('PATH').split(os.pathsep):
        if os.path.exists(os.path.join(path, command)):
            found += [path]

    return found    

def find_exe_in_path(command):
    '''
    First try and find the command in path, if that fails look for command.exe in path
    '''

    # Try and find the command in path
    found = find_in_path(command)

    # If we didn't find it, try command.exe
    if not found:
        found = find_in_path(command + '.exe')

    # If we still haven't found it, raise an exception
    if not found:
        raise ExecutableError('"%s" could not be found. Please supply the path to the %s executable.' % (command, command))
    else:
        executable_path = os.path.join(found[0], command)
        if len(found) > 1:
            print 'Multiple versions of %s found, using %s. If you wish to use a different version, please specify it explicitly' % (command,executable_path)
    return executable_path


from bilbo_core.models import File
