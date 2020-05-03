#! /home/brandon/.pyenv/versions/3.7.5

import os
import sys
import cv2
import numpy as np
#from matplotlib import pyplot as plt

import string_functions as s


class ImageCropper:
    def __init__(self, image=None, cropped_image=None):
        self.crop_text = (f"\tEnter 'c' to save image, "
                          f"'r' to redo crop selection, "
                          f"'q' to quit cropping.\n")
        if image and not cropped_image:
            self.initVariables(image)
            self.CROP()

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
        self.directory = os.path.dirname(cropped_image)
        self.template_name = os.path.basename(cropped_image)
        self.ext = get_file_extension(self.template_name)

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
    

    def CROP(self):
        print(self.crop_text)
        self.crop_image()
        if self.use_cropped_image_as_template():   # returns 'recrop' or None
            self.crop_new_template()
        return None

    # CROP
    # crop selection -> save image, restart or quit 
    def crop_image(self):
        """User selections region of interest for cropping image."""
        if self.crop_selection():   # returns 'copied' or None

            # returns 'saved', 'restart', or None
            save_value = self.await_save_image(self.cropped_image)

            if save_value == 'restart':
                self.crop_image()

        return None

    # use mouse to make a section for cropping
    def crop_selection(self):
        title = "select area for cropping"
        cv2.namedWindow(title)
        cv2.setMouseCallback(title, self.shape_selection, self.image)

        while True:
            cv2.imshow(title, self.image)
            key = cv2.waitKey(20) & 0xFF

            # start fresh with new image
            if key == ord("r"):
                self.image = self.clone.copy()
                cv2.setMouseCallback(title, self.shape_selection, self.image)

            # copy the crop selection
            elif key == ord("c"):
                self.image = self.clone.copy()

                if self.image_cropped():        # cropped image saved
                    return 'copied'

            # don't crop image and exit
            elif key == ord("q"):
                break

        cv2.destroyAllWindows()
        return None

    # copy the section outlined by user
    def image_cropped(self):
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

    # wait for input key to save image (or not), or to restarts
    # return 'saved', 'restart', or None
    def await_save_image(self, image):
        key = self.wait_for_key_input(image, ['c', 'q', 'r'], title='save image or not')
        cv2.destroyAllWindows()
        
        # save the cropped image
        if key == ord('c'):
            self.template_path = save_image_(self.directory, self.filename, '_cropped', image)
            return 'saved'
            
        # don't save cropped image
        elif key == ord('q'):
            print("quitting crop selection save image")

        # restart the crop selection
        elif key == ord('r'):
            return 'restart'

        return None

    # CROP
    # use cropped image as template
    def use_cropped_image_as_template(self):
        # user uses cropped image as template
        if self.cropped_image_used_as_template():
            return self.crop_other_images()

        else:
            return None

    # ask user if they would like to use cropped image as template
    def cropped_image_used_as_template(self):
        """Ask user if they would like to use this cropped image as template."""
        confirmed = ask_for_confirmation("\tUse cropped image as a template? ")
        return confirmed

    # crop images with inside directory using template (cropped image)
    def crop_other_images(self):
        self.initTemplateVariables(self.template_path)
        # adds files (to self.images_to_compare) that don't have a cropped version
        self.find_other_images_in_directory()

        # TEMPLATE MATCHING
        for image in self.images_to_compare:
            self.match_template(image)
        
        # UNCROPPED FILES - Reselect Template
        if self.uncropped_images:
            return 'recrop new template'

        return None


    # CROP
    # reselect template (recrop) from first index of self.uncropped_images 
    def crop_new_template(self):
        """Reselect a template (and filter) for matching."""
        self.initVariables(self.uncropped_images[0])
        text = f"\tWould you like to use multiple filters for matching template? "
        confirmed = ask_for_confirmation(text)

        if confirmed:
            self.RECROP_NEW_TEMPLATE()
        else:
            self.CROP()

        return None

    # cropping a new template to be used with multiple methods of template matching
    def RECROP_NEW_TEMPLATE(self):
        print(self.crop_text)
        if self.recrop_image():     # return 'saved' or None
            if self.multi_method_crop_other_images() == 'uncropped images':
                self.crop_new_template()
        return None


    # RECROP
    # crop a new template for matching
    def recrop_image(self):
        if self.crop_selection():    # return 'copied' or None

            # return 'saved', 'restart', or None
            save_value = self.await_save_image(self.cropped_image)

            if save_value == 'restart':
                self.recrop_image()

            elif save_value == 'saved':
                return 'saved'

        return None


    # RECROP
    # crop other images in directory with new template
    def multi_method_crop_other_images(self):
        # compare templates
        self.initTemplateVariables(self.template_path)
        self.find_other_images_in_directory()

        # template matching
        for image in self.images_to_compare:
            self.template_matching_multiple_methods(image)

        # select another template to match with
        if self.uncropped_images:
            return 'uncropped images'

        return None

    # match template using multiple methods 
    def template_matching_multiple_methods(self, comparison_image):
        """
        Goes through multiple methods of template matching.
        
        If one of the methods provides a cropped image that is satisfactory,
            save that cropped image.
        else
        """
        # reimplement template_matching()
        # go through different methods
        # select one method that satisfies the current template matching.
        img = open_image(comparison_image)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filename = os.path.basename(comparison_image)

        #methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 
        #             'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF']
        methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
                   'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
        methods_used = []
        print(f"\tmatching template with multiple methods")
        for meth in methods:
            method = eval(meth)
            print(meth)
            print("press 'c' to save image or 'q'/'r' to continue")
            title = f"method: {meth}, press c to save!"

            # template matching
            res = cv2.matchTemplate(img_gray, self.template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc

            else:
                top_left = max_loc

            bottom_right = (top_left[0] + self.w, top_left[1] + self.h)
            x1, y1 = top_left
            x2, y2 = bottom_right
            crop_img = img[y1:y2, x1:x2]
            
            key = self.wait_for_key_input(crop_img, ['c', 'q', 'r'], title=title)
            cv2.destroyAllWindows()

            # user choose to save cropped image
            if key == ord('c'):
                # don't keep track of this file if the cropped image is satisfactory
                methods_used = []
                save_image_(self.directory, filename, '_cropped', crop_img)
                break

        # reject cropped version of this image
        if key != ord('c'):
            self.uncropped_images += [comparison_image]
        
        return None  


    def find_other_images_in_directory(self):
        """Sets"""
        files = find_files(self.directory, self.ext)
        new_files = []

        for folderName, subfolders, filenames in os.walk(self.directory):
            for filename in filenames:
                # filename not having a 'cropped' version returns filepath, otherwise None
                path = uncropped_filepath(self.directory, filename, files)
                if path:
                    new_files += [path]
        self.images_to_compare = new_files
        return None

    # template matching function
    def match_template(self, comparison_image):
        self.comparison_path = comparison_image

        img = cv2.imread(comparison_image)
        img_gray = cv2.imread(comparison_image, 0)

        # match template function; filter = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(img_gray, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # best match location
        top_left = max_loc
        bottom_right = (top_left[0] + self.w, top_left[1] + self.h)

        x1, y1 = top_left
        x2, y2 = bottom_right
        cropped_img = img[y1:y2, x1:x2] 
        self.await_template_save_image(cropped_img)

        return None

    # wait for key input for new cropped image
    def await_template_save_image(self, image):
        key = self.wait_for_key_input(image, ['c', 'q', 'r'])

        # save the cropped image
        if key == ord('c'):
            temp_filename = os.path.basename(self.comparison_path)
            save_image_(self.directory, temp_filename, '_cropped', image)

        # don't save cropped image
        elif key == ord('q'):
            print("discarding image")

        # don't save cropped image
        elif key == ord('r'):
            self.uncropped_images += [self.comparison_path]
        
        cv2.destroyAllWindows()
        return None

    # wait 10 milliseconds for key input while showing image
    def wait_for_key_input(self, image, args, title="crop_img"):
        """Return inputted key value."""
        print(self.crop_text)
        cv2.namedWindow(title)
        while True:
            # display the image and wait for a keypress
            cv2.imshow(title, image)
            key = cv2.waitKey(10) & 0xFF

            for arg in args:
                if key == ord(arg):
                    return key
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

# find files inside directory, with optional extension & exclude_string
def find_files(directory, ext=None, exclude_string=None):
    """
    Find files inside directory with extension given.
    """
    # directory = os.getcwd()
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
    print(f"\t\tanswer is: {answer}")
    answer = s.remove_whitespace_at_either_end(answer)
    if answer.lower() in affirmative:
        return True
    else:
        return False


def main():
    pass

if __name__ == '__main__':
    main()
    sys.exit()