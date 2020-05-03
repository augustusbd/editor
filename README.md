# Editor - Image Cropper (Python)

The main objective of this project is to create a program that will act as an editor of sorts. It will go through an user's files, making changes to files as it seems fit. Project is being developed on Ubuntu 16.04.

The first iteration of this program will crop multiple images using a template chosen by user.

In the future, Editor will go through correcting mistakes in notes and logging them, backing up files on a schedule, and more tasks as I imagine them.


To Run:

        Image Cropping
	$ python editor.py -i image_location
	$ python editor.py --image image_location 

        File Editor
	$ python editor.py -fe rename


Arguments for 'editor.py' file:

Image Cropping:

	-i, --image IMAGE: 
		give a path to a image, to make a crop selection from image.

	-ic, --image_crop [IMAGE_CROP [IMAGE_CROP ...]]: 
		give a path to a cropped image, to use as a template


Editing Files:

	-fe, --edit_file FILE_EDIT:
		give an argument to do one of the following (options for now):
			rename  - rename files
			

