import os,random,string
            
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

def get_state(directory):
    files = set()
    for path in os.listdir(directory):
        details = os.stat(path)
        files.add((path,details.st_atime,details.st_mtime,details.st_ctime))
    return files

def get_changed_files(directory,old_state):
    new_state = get_state(directory)
    changed = new_state.difference(old_state)
    changed_files = set()
    for path,atime,mtime,ctime in changed:
        abs_path = os.path.abspath(path)
        file_object = File.get_from_current_host(abs_path)
        changed_files.add(file_object)
    return changed_files

def move_new_files(directory):
    new_files = set()
    for path in os.listdir(directory):
        old_path = os.path.abspath(os.path.join(directory,path))
        new_path = os.path.abspath(os.path.join(os.getcwd(),path))
        try:
            os.renames(old_path,new_path)
        except OSError:
            os.remove(new_path)
            os.rename(old_path,new_path)
        file_object = File.get_from_current_host(new_path)
        new_files.add(file_object)
    return new_files

def unique_filename_in(path=None):
    """Return a random filename unique in the given path.

    The filename returned is twenty alphanumeric characters which are
    not already serving as a filename in *path*. If *path* is
    omitted, it defaults to the current working directory.
    """
    if path == None:
        path = os.getcwd()
    path = os.path.abspath(path)
        
    def random_string():
        return "".join([random.choice(string.letters + string.digits)
                        for x in range(20)])
    while True:
        filename = random_string()
        files = [f for f in os.listdir(path) if f.startswith(filename)]
        if files == []:
            break
    return filename

from bilbo_core.models import File,Host
