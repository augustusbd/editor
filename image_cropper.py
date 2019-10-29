#! /home/brandon/.pyenv/versions/3.7.5

import os
import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt


class ImageCropper:
    def __init__(self, image, cropped_image=None):
        self.initVariables(image)
        self.crop_text = (f"Enter 'c' to save image, "
                          f"'r' to redo crop selection, "
                          f"'q' to quit cropping.")

        if cropped_image == None:
            self.await_crop_selection()
        else:
            self.initTemplateVariables(cropped_image)
            self.use_cropped_image_as_template()

    def initVariables(self, image):
        self.ref_point = []            # initialize the list of reference points
        self.file_path = image
        self.filename = os.path.basename(image)
        self.directory = os.path.dirname(image)
        self.ext = get_file_extension(self.filename)

        self.image = cv2.imread(image)
        self.clone = self.image.copy()
        self.shape = self.image.shape


    def initTemplateVariables(self, cropped_image):
        self.template_path = cropped_image
        self.template = cv2.imread(self.template_path, 0)
        self.w, self.h = self.template.shape[::-1]
        self.uncropped_images = []
        self.images_to_compare = []


    # mouse callback function
    def shape_selection(self, event, x, y, flags, param):
        """Selects region of interest in image window."""
        blue = (255, 0, 0)
        green = (0, 255, 0)
        # if the left mouse button was clicked, 
        # record the starting (x, y) coordinates
        if event == cv2.EVENT_LBUTTONDOWN:
            self.ref_point = [(x, y)]
            # draw a circle around the starting coordinate
            cv2.circle(param, (x,y), 5, blue, -1)
            
        # the left mouse button was released
        # record the ending (x, y) coordinates
        elif event == cv2.EVENT_LBUTTONUP:
            self.ref_point.append((x, y))
            # draw a rectangle around the region of interest
            cv2.rectangle(param, self.ref_point[0], self.ref_point[1], green, 2)
            
    # use mouse to make a section for cropping
    def await_crop_selection(self):
        print(f"select area for cropping")
        print(self.crop_text)
        cv2.namedWindow("image")
        # setup mouse callback function
        cv2.setMouseCallback("image", self.shape_selection, self.image)
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", self.image)
            key = cv2.waitKey(20) & 0xFF

            # if the 'r' key is pressed, reset the cropping region
            if key == ord("r"):
                print("reseting the image")
                self.image = self.clone.copy()
                cv2.setMouseCallback("image", self.shape_selection, self.image)

            # if the 'c' key is pressed, copy the crop selection
            elif key == ord("c"):
                self.image = self.clone.copy()
                if self.copy_crop_section() != None:
                    self.await_save_image(self.cropped_image)
                break

            # if the 'q' key is pressed, don't crop image and exit
            elif key == ord("q"):
                cv2.destroyAllWindows()
                print("quitting crop selection")
                break

        return None

    # copy the section outlined by user
    def copy_crop_section(self):
        """Crop the region of interest."""
        print("copying crop selection")
        # if there are two reference points, then crop the region of interest
        if len(self.ref_point) == 2:
            print(self.crop_text)
            cv2.destroyAllWindows()

            # reference points for Region of Interest
            x1, y1 = self.ref_point[0]
            x2, y2 = self.ref_point[1]

            self.cropped_image = self.clone[y1:y2, x1:x2]
            return 'copied'

        return None

    # wait for input key to save image (or not), or to restart
    def await_save_image(self, image):
        key = self.wait_for_key_input(image, 'c', 'q', 'r')
        
        # if the 'c' key is pressed, save the cropped image
        if key == ord('c'):
            print("saving image")
            self.template_path = save_image_(self.directory, self.filename, '_cropped', image)
            self.use_cropped_image_as_template()

        # if the 'q' key is pressed, don't save cropped image
        elif key == ord('q'):
            print("quitting crop selection save image")

        # if the 'r' key is pressed, restart the crop selection
        elif key == ord('r'):
            print("restarting")
            self.await_crop_selection()

        cv2.destroyAllWindows()
        return None

    # ask user if they would like to use cropped image as template
    def use_cropped_image_as_template(self):
        """Ask user if they would like to use this cropped image as template."""
        cv2.destroyAllWindows()
        confirmed = ask_for_confirmation("Use cropped image as template? ")
        if confirmed:
            self.crop_other_images()
        return None

    # crop images with inside directory using template (cropped image)
    def crop_other_images(self):
        # compare templates
        print(f"cropping other images")
        self.initTemplateVariables(self.template_path)
        self.find_other_images_in_directory()

        # TEMPLATE MATCHING
        for image in self.images_to_compare:
            #template_matching(other_images[0], self.template)
            print(f"\ttemplate matching")
            self.match_template(image)
        
        # UNCROPPED FILES - Reselect Template
        if len(self.uncropped_images) > 0:
            self.recrop_template()

        return None


    def find_other_images_in_directory(self):
        """Sets"""
        files = find_files(self.directory, self.ext)
        new_files = []

        # goes through files in directory,
        # adding files that don't have a cropped version to new list of files
        for folderName, subfolders, filenames in os.walk(self.directory):
            for filename in filenames:
                # if filename does not have 'cropped' version, get filepath
                path = uncropped_filepath(self.directory, filename, files)
                if path != None:
                    new_files += [path]
        self.images_to_compare = new_files
        return None

    # template matching function
    def match_template(self, comparison_image):
        self.comparison_path = comparison_image

        img = cv2.imread(comparison_image)
        img_gray = cv2.imread(comparison_image, 0)

        # actual match template function; filter = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(img_gray, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # best match location
        top_left = max_loc
        bottom_right = (top_left[0] + self.w, top_left[1] + self.h)
        cv2.rectangle(img_gray,top_left, bottom_right, 255, 2)

        x1, y1 = top_left
        x2, y2 = bottom_right
        cropped_img = img[y1:y2, x1:x2] 
        self.await_template_save_image(cropped_img)

        return None

    # wait for key input for new cropped image
    def await_template_save_image(self, image):
        key = self.wait_for_key_input(image, 'c', 'q', 'r')

        # if the 'c' key is pressed, save the cropped image
        if key == ord('c'):
            print("saving auto-cropped image")
            temp_filename = os.path.basename(self.comparison_path)
            save_image_(self.directory, temp_filename, '_cropped', image)

        # if the 'q' key is pressed, don't save cropped image
        elif key == ord('q'):
            print("discarding image")

        # if the 'r' key is pressed, don't save cropped image
        elif key == ord('r'):
            print(f"redo crop selection for {self.comparison_path}")
            self.uncropped_images += [self.comparison_path]
        
        cv2.destroyAllWindows()
        return None

    # reselect template (recrop) from first index of self.uncropped_images 
    def recrop_template(self):
        """Reselect a template (and filter) for matching."""
        self.initVariables(self.uncropped_images[0])
        text = f"Would you like to use a different filter for matching template? "
        confirmed = ask_for_confirmation(text)
        if confirmed:
            self.reselect_crop_section()
        else:
            self.await_crop_selection()

        return None

    # crop a new template and use different filters to match
    # user selects another section to crop
    def reselect_crop_section(self):
        """Alternative Await Shape Selection Function."""
        print(f"reselecting template image")
        print(self.crop_text)
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.shape_selection, self.image)
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", self.image)
            key = cv2.waitKey(20) & 0xFF

            # if the 'c' key is pressed, copy the crop selection
            if key == ord('c'):
                self.image = self.clone.copy()
                if self.copy_crop_section() != None:
                    self.await_input_to_save_image(self.cropped_image)
                break

            # if the 'q' key is pressed, don't crop image and exit
            elif key == ord('q'):
                print(f"quitting recrop selection")
                break

            # if the 'r' key is pressed, restart the crop selection
            elif key == ord('r'):
                print(f"restarting recrop selection")
                self.image = self.clone.copy()
                cv2.setMouseCallback("image", self.shape_selection, self.image)
                
        cv2.destroyAllWindows()
        return None

    # multiple methods -template matching
    # wait for input to save image, or quit, or restart selection
    def await_input_to_save_image(self, image):
        key = self.wait_for_key_input(image, 'c', 'q', 'r')

        # if the 'c' key is pressed, save the cropped image
        if key == ord('c'):
            print("saving recropped image")
            self.template_path = save_image_(self.directory, self.filename, '_cropped', image)
            cv2.destroyAllWindows()
            self.recrop_other_images()

        # if the 'q' key is pressed, don't save cropped image
        elif key == ord('q'):
            print("quitting recrop selection save")

        # if the 'r' key is pressed, restart the crop selection
        elif key == ord('r'):
            print("restarting recrop selection")
            self.reselect_crop_section()
        
        cv2.destroyAllWindows()
        return None

    # crop other images in directory with new template
    def recrop_other_images(self):
        # compare templates
        print(f"recropping other images")
        self.initTemplateVariables(self.template_path)

        # adds files to (self.images_to_compare) that don't have a cropped version
        self.find_other_images_in_directory()
        self.methods_to_use = {}
        # template matching
        for image in self.images_to_compare:
            self.template_matching_multiple_methods(image)
            print(self.methods_to_use)
        return None

    # match template using multiple methods 
    def template_matching_multiple_methods(self, image):
        # reimplement template_matching()
        # go through different methods
        # select one method that satisfies the current template matching.
        img = open_image(image)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        #methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 
        #             'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF']
        methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
                   'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
        methods_used = []
        print(f"\tmatching template with multiple methods")
        for meth in methods:
            method = eval(meth)
            print(meth)

            # template matching
            res = cv2.matchTemplate(img_gray, self.template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc

            else:
                top_left = max_loc

            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(img_gray,top_left, bottom_right, 255, 2)

            plt.imshow(img_gray, cmap='gray')
            plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
            plt.suptitle(meth)
            plt.show()

            title = f"template match with method: {meth}"
            cv2.namedWindow(title)
            cv2.imshow(title, img_gray)
            key = cv2.waitKey(0) & 0xFF
            print(f"key has value: {key}")
            cv2.destroyAllWindows()

            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            confirmed = ask_for_confirmation(f"Does this method, {meth}, work? ")
            if confirmed:
                methods_used.append(meth)

        self.methods_to_use.update({image:methods_used})
        return None

    # wait 10 milliseconds for key input on loop
    def wait_for_key_input(self, image, *argv, title="crop_img"):
        """Return inputted key value."""
        print(self.crop_text)
        while True:
            # display the image and wait for a keypress
            cv2.imshow(title, image)
            key = cv2.waitKey(10) & 0xFF

            for arg in argv:
                if key == ord(arg):
                    return key
        return None

    # template matching function - multiple filters
    # NOT USING
    def template_matching_recrop(self):
        # do template matching with different methods
        for image in self.uncropped_images:
            # reselect crop section
            self.reselect_cropping_section(image)
            # make new selection, template
            # redo template matching with new template

        #template_matching(self.comparison_path, self.template)
        template_matching_threshold(self.comparison_path, self.template, 0.3)
        confirmed = ask_for_confirmation("Do this crop selection satisfy you? ")
        if not confirmed:
            # use self.comparison_path for new crop selection
            self.reselect_cropping_section()
        return None


# save image with a string inserted into filename
def save_image_(directory, filename, add_string, image):
    """Save image with a string inserted before extension."""
    new_filename = insert_string_before_extension(filename, add_string)
    new_filepath = os.path.join(directory, new_filename)
    # save the image
    cv2.imwrite(new_filepath, image)
    return new_filepath


def template_matching_threshold(comparison_image, template, threshold=0.8):
    img_rgb = cv2.imread(comparison_image)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]
    green = (0, 255, 0)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res>=threshold)
    for point in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, point, (point[0] + w, point[1] + h), green, 1)
        #cv2.rectangle(param, ref_point[0], ref_point[1], green, 2)

    cv2.imshow("template threshold", img_gray)
    key = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()
    #if key == ord('c'):
        #print('A-okay')
        # save_image_('_cropped')
    return None

def template_matching(comparison_image, template):
    img = open_image(comparison_image)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]

    #methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
    #           'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF']
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

    for meth in methods:
        print(meth)
        method = eval(meth)

        # Apply template Matching
        res = cv2.matchTemplate(img_gray,template,method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc

        else:
            top_left = max_loc

        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(img_gray,top_left, bottom_right, 255, 2)

        #plt.imshow(img_gray, cmap='gray')
        #plt.title('Detected Point'), plt.xticks([]), plt.yticks([])

        #plt.suptitle(meth)
        #plt.show()
        cv2.imshow('template match', img_gray)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return None

def find_files_without_a_cropped_version(directory, ext):
    files = find_files(directory, ext)
    new_files = []

    for folderName, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            # returns a file without a cropped image version; otherwise None
            path = uncropped_filepath(directory, filename, files)
            # the path contains a file without a cropped version in directory
            if path != None:
                new_files += [path]

    return new_files
                
def uncropped_filepath(directory, filename, files):
    """Return filepath that does not include a cropped version of a file."""
    filepath = os.path.join(directory, filename)

    # file is not a cropped image
    if 'crop' not in filename:
        new_filename = insert_string_before_extension(filename, '_cropped')
        new_filepath = os.path.join(directory, new_filename)

        # there isn't a cropped version of this file; return file path
        if new_filepath not in files:
            return filepath

    return None

# basically os.path.basename(file_path)
def get_filename(file_path):
    seperators = file_path.count(os.sep)
    num_sep = 0 
    if num_sep == seperators:
        return file_path

    file_list = list(file_path)
    for index in range(len(file_list)):
        if file_list[index] == os.sep:
            num_sep += 1
        if num_sep == seperators:
            return file_path[index+1:]        # file name of path

# inserts a string into a string
def insert_string_before_extension(original, add_string):
    extension = get_file_extension(original)
    ext_len = len(extension)
    original_len = len(original)
    x = original_len - ext_len
    new_string = original[:x] + add_string + extension
    return new_string

# gets the file extension of a file
def get_file_extension(file):
    file = list(file)
    reverse_extension = []
    for i in reversed(file):
        reverse_extension += [i]
        if i == '.':
            break

    extension = ''
    for j in reversed(reverse_extension):
        extension += j
    return extension

# returns a numpy object containing image
def open_image(image):
    if type(image) != type(str()):
        return image
    # the image is actually a file location
    else:
        return cv2.imread(image)

# mouse callback function
def shape_selection(event, x, y, flags, param):
    # grab references to global variables
    global ref_point
    blue = (255, 0, 0)
    green = (0, 255, 0)

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cv2.circle(param, (x,y), 5, blue, -1)
        print(ref_point[0])

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        ref_point.append((x, y))
        # draw a rectangle around the region of interest
        cv2.rectangle(param, ref_point[0], ref_point[1], green, 2)
        print(ref_point[1])

def crop_image():
    # load the image, clone it, and setup the mouse callback function
    image = cv2.imread('./pics/Screenshot from 2019-10-26 02-49-37.png')
    clone = image.copy()

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", shape_selection, image)

    # keep looping until the 'q' key is pressed
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", image)
        key = cv2.waitKey(20) & 0xFF 

        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            image = clone.copy()
            cv2.setMouseCallback("image", shape_selection, image)

        elif key == ord("q"):
            break

    # if there are two reference points, then crop the region of interest
    # from teh image and display it
    if len(ref_point) == 2:
        print("cropping image")
        crop_img = clone[ref_point[0][1]:ref_point[1][1], ref_point[0][0]:ref_point[1][0]]
        cv2.imshow("crop_img", crop_img)
        key = cv2.waitKey(0) & 0xFF

        if key == ord('c'):
            print("saving image")
            cv2.imwrite('./pictures/saved_image.png', crop_img)

    # close all open windows
    cv2.destroyAllWindows()

def crop_other_files(crop_img):
    # go through directory and find files with same extension
    # find the template that matches crop_img
    # crop the template and save file
    # repeat until no more images (that don't already have a crop)
    pass

def matching_images(crop_img, img):
    # match the template of crop_img to img
    pass

directory = os.getcwd()
def find_files(directory, ext, exclude_string=None):
    """
    Find files inside directory with extension given.
    """
    files = []
    for folderName, subfolders, filenames in os.walk(directory):
        #print(f"The current folder is {folderName}")
        #for subfolder in subfolders:
            #print(f"SUBFOLDER OF {folderName}: {subfolder}")
        for filename in filenames:
            #print(f"FILE INSIDE {folderName}: {filename}")
            if (exclude_string == None) and filename.endswith(ext):
                filepath = os.path.join(folderName, filename)
                files.append(filepath)
                #print(filepath)
            elif (exclude_string not in filename) and filename.endswith(ext):
                filepath = os.path.join(folderName, filename)
                files.append(filepath)
    return files


def ask_for_confirmation(text):
    """Ask a user if they would like to do something or not. Returns True or False."""
    affirmative = ['yes','ya','ye','y','oui','si','mhm','mmhmm', '']
    answer = input(text)
    if answer.lower() in affirmative:
        return True
    else:
        return False



if __name__ == '__main__':
    crop()
    sys.exit()

