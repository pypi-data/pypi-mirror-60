#!/usr/bin/env python3

import re

from requests import get
from bs4 import BeautifulSoup



# class for an error if the user's reference is bad
class InvalidReference(Exception):
    pass


# function that 'snags' elements from the page located at url using CSS reference syntax
def S(pattern, url):
    source = get(url).content
    soup = BeautifulSoup(source, 'html.parser')

    # obviously this is going to be tricky so explained:
    # group 0 is the whole thing
    # group 1 is the element+selector+selected, e.g. div#container or span.right
    # group 3 is the selector, e.g. # or .
    # group 4 is the attribute, e.g. href (found inside square braces which are not a part of the group)
    regex = r'^(((\.|#)?[\w-]+)*)\[?([\w-]*)\]?$'
    pattern = re.match(regex, pattern)
    if not pattern:
        raise InvalidReference('The given string is not a valid CSS reference')


    element = pattern.group(1)                  # the DOM element itself
    selector = pattern.group(3) or element      # the # or .; will default to first char of element if nonexistent
    element = element[0:(len(element) if element == selector  else element.index(selector))] # element proper
    selected = pattern.group(2)                 # the name of the class or id selected
    if selected:
        selected = selected[1:]
    attribute = pattern.group(4)                # only return the element if this attribute is present if existent

    if selector == '.':
        if attribute:
            return soup.find_all(element or True, class_=selected, attrs={attribute: True})
        return soup.find_all(element or True, class_=selected)
    elif selector == '#':
        if attribute:
            return soup.find_all(element or True, id=selected, attrs={attribute: True})
        return soup.find_all(element or True, id=selected)
    return soup.find_all(element, attrs={attribute: True}) if attribute else soup.find_all(element)
