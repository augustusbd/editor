#!/home/brandon/.pyenv/versions/3.7.5/envs editor_env

import re
import os
import shutil
from os.path import join
from pathlib import Path

affirmative_answers = ['y', 'yes', 'ya', '']
home = str(Path.home())

def renameDateFormats(folder):
	"""Walk through files and change date tempaltes."""
	# Check rename_dates.py for updates
	for root, dirs, files in os.walk(folder):
		print(root, end='\n\n')

		dirs[:] = removeDirectories(dirs)
		changeDateFormat(root, files)

	return None

def removeDirectories(folders):
	"""Remove directories from use."""
	included_folders = readIncludedDirectories()
	excluded_folders = readExcludedDirectories()

	if len(folders) != 0:
		print("\t\t***DIRECTORIES***")

	for folder in folders:

		# Remove Hidden Directories
		if folder.startswith('.') or folder.endswith('~'):
			excluded_folders.add(folder)

		# Folder is not a part of excluded or included directories
		elif (folder not in included_folders) and (folder not in excluded_folders):
			answer = input(f"\t> ADD folder [{folder}] to included list? ")

			# Keep folder in list of directories
			if answer.lower() in affirmative_answers:
				included_folders.add(folder)
				print("\tadded to included list.\n")
			
			# Remove folder from list of directories
			else:
				excluded_folders.add(folder)
				print("\tadded to excluded list.\n")

	writeIncludedDirectories(included_folders)
	writeExcludedDirectories(excluded_folders)
	return included_folders

def changeDateFormat(root, files):
	"""Change date format in file name."""
	for file in files:
		new_file = checkDateFormat(file)

		if new_file != file: 
			print("\t\t***FILE***")
			answer = input(f"\t> Change [{file}] to [{new_file}]: ")

			if answer.lower() in affirmative_answers:
				print(f"\t> RENAMING [{file}] to [{new_file}]", end='\n\n')

				old_path = join(root, file)
				new_path = join(root, new_file)

				# BEFORE RENAMING
				# DETERMINE IF THERE IS ANYTHING AFTER NEW FILENAME
				# IF SO, ADD underscore after new date
				shutil.move(old_path, new_path)
			
			else:
				new_file = file
				print(f"\t> KEEPING [{file}]", end='\n\n')
	return None

_dateDigits = re.compile('\d\d\d\d\d\d\d\d') # 'YYYYMMDD'
def checkDateFormat(filename):
	"""Check if a file name contains 8 digits in sequence."""
	dateInFileName = _dateDigits.search(filename)

	if dateInFileName:
		start, end = dateInFileName.span()
		date = filename[start:end]

		new_date = insertDateTemplate(date)
		new_filename = filename.replace(date, new_date)

		return new_filename
	return filename

def insertDateTemplate(date):
	"""Change YYYYMMDD to YYYY-MM-DD."""
	new_date = (date[0:4] + "-" + 
			    date[4:6] + "-" + 
			    date[6:8])
	return new_date

def readIncludedDirectories():
	included = set()
	try:
		with open('include_directories.txt', 'r') as f:
			for line in f:
				line = line.replace('\n', '')
				included.add(line)
		return included

	except IOError:
		return set('')

def writeIncludedDirectories(included_folders):
	with open('include_directories.txt', 'w') as f:
		for folder in included_folders:
			f.write(f"{folder}\n")
	return None

def readExcludedDirectories():
	excluded = set()
	try:
		with open('exclude_directories.txt', 'r') as f:
			for line in f:
				line = line.replace('\n', '')
				excluded.add(line)
		return excluded

	except IOError:
		return set('')

def writeExcludedDirectories(excluded_folders):
	with open('exclude_directories.txt', 'w') as f:
		for folder in excluded_folders:
			f.write(f"{folder}\n")
	return None