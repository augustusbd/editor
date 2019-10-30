from collections.abc import Iterable

#	string functions #
def add_strings_together_from_list(a_list):
    """
    Return a string comprised from list indices. List must be comprised of strings.
    """
    text = ""
    if is_every_index_a_string(a_list):
        for value in a_list:
            text = text + value + " "
        text = remove_whitespace_at_either_end(text)
        return text
    else:
        print("This list contains an element that is not a string.")
        confirmed = ask_for_confirmation("Would you like to keep the first element? ")
        if confirmed:
            return a_list[0]
        else:
            return a_list

def capitalize_each_word(text):
    new_string = ""
    for word in text.split():
        new_string = new_string + word.capitalize() + " "
    new_string = remove_whitespace_at_either_end(new_string)
    return new_string

def different_versions_of_string(text):
    """
    Returns a list containing the different versions of a string.
    ex: text = 'continue'
        'continue' can be written as 'Continue', 'CONTINUE', 'cont.', 'CONT.'
    """
    string_list = [text, text.upper(), text.capitalize(), capitalize_each_word(text)]
    return string_list

def is_every_index_a_string(a_list):
    """
    Returns True if every element in a_list is a string. Otherwise returns False.
    """
    for item in a_list:
        if type(item) != str:
            return False
    return True

def put_strings_together(a_list):
    """
    Return a string comprised from list indices. List must be comprised of strings.
    """
    # determines if a_list is an iterable object or not
    if not isinstance(a_list, Iterable):
        return a_list

    text = ""
    if is_every_index_a_string(a_list):
        for value in a_list:
            text = text + value + " "
        text = remove_whitespace_at_either_end(text)
        return text
    else:
        print("This list contains an element that is not a string.")
        print("Returning the first element of list.")
        return a_list[0]


#		whitespace
def has_non_space_whitespace(text):
    """Returns True if text has non-space whitespace."""
    whitespace = ['\n','\t','\r','\x0b','\x0c']
    for x in whitespace:
        if x in text:
            return True
    return False

def remove_non_space_whitespace(text):
    """Takes out whitespace that isn't a space ' '."""
    whitespace = ['\n','\t','\r','\x0b','\x0c']
    if type(text) != str:
        print("Argument is not a string.")    
    else:
        while has_non_space_whitespace(text):
            for x in whitespace:
                text_index = text.find(x)
                if text_index != -1:
                    text = text[:text_index] + text[text_index+1:]
    return text

def remove_whitespace_at_either_end(text):
    """Takes out whitespace at the start and end of a text."""
    whitespace = ['\n','\t',' ']
    if type(text) != str:
        print("Argument is not a string.")
    else:
        while starts_or_ends_with_whitespace(text):
            for x in whitespace:
                if text.startswith(x):
                    text = text[1:]
                if text.endswith(x):
                    text = text[:-1]
    return text

def starts_or_ends_with_whitespace(text):
    """Returns True if text starts or ends with whitespace."""
    whitespace = ['\n','\t',' ','\r','\x0b','\x0c']
    for x in whitespace:
        if text.startswith(x):
            return True
        elif text.endswith(x):
            return True
    return False