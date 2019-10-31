#! /home/brandon/.pyenv/versions/3.7.5
# EDITOR


import sys
import argparse

import image_cropper as ic
import file_editor as fe
import string_functions as s

# construct the argument parser and parse the arguments
parser = argparse.ArgumentParser()
# argument for cropping an image
parser.add_argument('-i', '--image', nargs='*', help='image path for cropping')
parser.add_argument('-ic', '--image_crop', nargs='*',
					help='cropped image path to use as a template')
parser.add_argument('-fe', '--file_edit', nargs='*',
					help='path of file to be edited')
#force_args = vars(parser.parse_args('-ic ./pics/Screenshot from 2019-10-26 02-49-37_cropped.png'))
args = vars(parser.parse_args())



def main(arg_dict):
	# -i or -ic arguments were used in command-line argument
	if (args['image'] != None) or (args['image_crop'] != None):
		image = s.put_strings_together(args['image'])
		image_crop = s.put_strings_together(args['image_crop'])

		print(f"image has value of : {image}")
		print(f"image_crop has value of : {image_crop}")

		image = ic.ImageCropper(image, image_crop)

	# other optional arguments will come later
	elif args['file_edit'] != None:
		file_path = s.put_strings_together(args['file_edit'])
		file = fe.FileEdit(file_path)
	
	return None

if __name__ == '__main__':
    main(args)
    sys.exit()

