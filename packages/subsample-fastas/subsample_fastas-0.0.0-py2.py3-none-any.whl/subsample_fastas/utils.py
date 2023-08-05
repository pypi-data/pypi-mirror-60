from os import makedirs
from os.path import isdir


def is_valid_dir(dirpath):
    """Return True if directory exists or can be created (then create it)
    
    Args:
        dirpath (str): path of directory
    Returns:
        bool: True if dir exists, False otherwise
    """
    if not isdir(dirpath):
        try:
            makedirs(dirpath)
            return True
        except OSError:
            return False
    else:
        return True
