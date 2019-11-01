#! /home/brandon/.pyenv/versions/3.7.5

# Editor - File Editor
import os
import shutil

import string_functions as s
import file_functions as f

# Edit A File
class FileEdit:
    def __init__(self, file_path):
        self.file = file_path
        with open(file_path) as file:
            self.data = file.readlines()

        self.ask_what_to_do_with_file()

    def ask_what_to_do_with_file(self):
        choices = ['remove items', 'rename files']
        text = f"What would you like to do with the file? "
        choice = s.user_input_choice(text, choices)
        if choice == 'remove items':
            self.remove_items()
        elif choice == 'rename files':
            self.edit()

    def remove_items(self):
        """Removes certain items from file."""
        # for now, only remove first 4 characters in each line
        self.remove_4_characters()
        self.write_new_data()
        return None
        
    
    def remove_4_characters(self):
        """Remove the first 4 characters per line of data."""
        self.new_data = []
        for line in self.data:
            if len(line) > 1:   # \n, \t count as 1 character
                new_line = line[4:]
                if len(new_line) == 0:
                    self.new_data.append('\n')
                else:
                    self.new_data.append(new_line)
            else:
                self.new_data.append(line)
        return None


    def write_new_data(self):
        with open(self.file, 'w') as file:
            for line in self.new_data:
                file.write(line)
        return None


    def edit(self):
        print("Editing the file!")
        return None


# File Handler
class FileHandler:
    def __init__(self):
        self.give_options()


    def give_options(self):
        choices = ['remove items', 'rename files']
        text = f"What would you like to do with the file? "
        choice = s.user_input_choice(text, choices)
        if choice == 'remove items':
            self.remove_items()
        elif choice == 'rename files':
            self.rename_files()

    def rename_files(self):
        folder_location = input("Enter file location of the files to rename: ")
        files = find_files(folder_location)
        rename_template = input("Enter the way you want to rename the files: ")
        new_location = input("Enter the new location of file. '.' for current directory: ")

        # simple for now:
        # rename them to one name with the added "file number"
        rename_alphanumberical(files, rename_template, new_location)


def rename_alphanumberical(files, new_name, new_location):
    """Simple rename with an increasing index for each file added."""
    for x in range(len(files)):
        if len(str(x)) < 2:
            add = "0" + str(x)
        else:
            add = str(x)
        filepath = os.path.join(new_location, new_name+add)
        shutil.move(files[x], filepath)




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