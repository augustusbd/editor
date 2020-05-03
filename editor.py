#! /home/brandon/.pyenv/versions/3.7.5
# EDITOR


import sys
import argparse

import image_cropper as icrop
import file_editor as fedit
import string_functions as s

# construct the argument parser and parse the arguments
parser = argparse.ArgumentParser()

# crop an image argument
parser.add_argument('-i', '--image', nargs='*', help='image path for cropping')

# cropped image template argument
parser.add_argument('-ic', '--image_crop', nargs='*',
					help='cropped image path to use as a template')

# file editor argument
parser.add_argument('-fe', '--edit_file', default=argparse.SUPPRESS,
					help='enter type of file edit to perform: remove or rename')

#force_args = vars(parser.parse_args('-ic ./pics/Screenshot from 2019-10-26 02-49-37_cropped.png'))
args = vars(parser.parse_args())	# put arguments and values into a dictionary



def main(arg_dict):

	# -i or -ic arguments were used in command-line argument
	if (args['image'] != None) or (args['image_crop'] != None):

		image = s.put_strings_together(args['image'])
		image_crop = s.put_strings_together(args['image_crop'])

		print(f"image has value of : {image}")
		print(f"image_crop has value of : {image_crop}")

		image = icrop.ImageCropper(image, image_crop)

	# -fe arguments in command-line
	elif args['edit_file'] == 'rename':
		fedit.rename_what()

	# other optional arguments will come later
	return None

if __name__ == '__main__':
    main(args)
    sys.exit()

