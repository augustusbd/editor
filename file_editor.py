#! /home/brandon/.pyenv/versions/3.7.5

# Editor - File Editor
import string_functions as s

# Edit A File
class FileEdit:
	def __init__(self, file_path):
		self.file = file_path
		with open(file_path) as file:
			self.data = file.readlines()

		self.ask_what_to_do_with_file()

	def ask_what_to_do_with_file(self):
		choices = ['remove items', 'edit']
		text = f"What would you like to do with the file? "
		choice = s.user_input_choice(text, choices)
		if choice != 'edit':
			self.remove_items()
		else:
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
			if len(line) > 1:	# \n, \t count as 1 character
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

# Mass Rename Files