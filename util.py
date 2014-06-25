import re
import keyword

import labscript

def is_valid_name(name, namespaces=()):
    """ Raises error if name is a Python keyword, an invalid identifier, or exists in any of the supplied namespaces. """
    # FIXME: better to return True/False rather than raising here?

    for namespace in namespaces:
        if name in namespace:
            raise labscript.LabscriptError("The device name '%s' already exists in the Python namespace. Please choose a different name." % name)

    if name in keyword.kwlist:
        raise labscript.LabscriptError("%s is a reserved Python keyword. Please choose a different name." % name)

    if not re.match(r'[a-z_]\w*$', name, re.I):
        raise labscript.LabscriptError("%s is not a valid Python variable name. Please choose a different name" % name)

                 
