#! /home/brandon/.pyenv/versions/3.7.5

import os

def find_files(directory, ext=None, exclude_string=None):
    """
    Find files inside directory.
        filter out files with extension and exlcuding string inside filename
    """
    # directory = os.getcwd()
    files = []
    for folderName, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            
            file = file_parameters(filename, ext, exclude_string)
            if file != None:
                filepath = os.path.join(folderName, file)
                files.append(filepath)
    return files

def file_parameters(filename, extension=None, exclude_string=None):
    """Returns a filename depending on the parameters."""
    if extension and exclude_string:
        if (exclude_string not in filename) and filename.endswith(ext):
            return filename

    elif extension and not exclude_string:
        if filename.endswith(extension):
            return filename

    elif not extension and exclude_string:
        if exclude_string not in filename:
            return filename

    else:
        return filename

    return None
