# -*- coding: UTF-8 -*-
#####################################################################
#                                                                   #
# UnitConversionBase.py                                             #
#                                                                   #
# Copyright 2013, Monash University                                 #
#                                                                   #
# This file is part of the labscript suite (see                     #
# http://labscriptsuite.org) and is licensed under the Simplified   #
# BSD License. See the license.txt file in the root of the project  #
# for the full license.                                             #
#                                                                   #
#####################################################################

import math
import re

from numpy import iterable, array

class UndefinedConversionError(Exception):
    pass

def vectorise(method):
    def f(instance, arg):
        # many things are iterables including strings, this needs revision
        if iterable(arg):
            return array([method(instance, el) for el in arg])
        else:
            return method(instance, arg)
    return f


si_prefix_symbols = ('Y','Z','E','P','T','G','M','k','','m',('u',u'µ'),'n','p','f','a','z','y')
si_prefix_multipliers = [10**-x for x in range(-24, 25, 3)]
si_prefixes = dict(zip(si_prefix_symbols, si_prefix_multipliers))

def parse_quantity(quantity):
    """ Given some quantity parse out the value and unit. eg. "1 MHz" => (1, "MHz") """
    quantity = quantity.strip()
    unit_index = re.search('[A-Z]', quantity, re.IGNORECASE).start()
    
    return (quantity[:unit_index], quantity[unit_index:])


def magnitude_conversion(initial_quantity, final_unit):
    """ Change order of magnitude of given quantity.
    
        Examples
        --------
        magnitude_conversion("1.2MHz", "Hz") => 1.2e6
        magnitude_conversion("4 fm", "m") => 4e-15
    """

    initial_quantity, final_unit = initial_quantity.strip(), final_unit.strip()

    initial_value, initial_unit = parse_quantity(initial_quantity)

    # if supplied units are the same, no conversion to be done so return value
    if initial_unit == final_unit:
        return initial_value

    # ensure that units are the same (other than the order of magnitude)
    if (initial_unit[1:] != final_unit[1:]) and (initial_unit[1:] != final_unit) and (initial_unit != final_unit[1:]):
            raise UndefinedConversionError("{} and {} are different units, cannot do order of magnitude conversion".format(initial_unit, final_unit))

    if len(initial_unit) == len(final_unit):
        # if they are not the same (already tested) but have equal lengths, both
        # have some prefix (eg. GHz->MHz)
        initial_prefix, final_prefix = initial_unit[0], final_unit[0]

        # exponent is then 3*distance between these prefixes in the symbol list
        try:
            multiplier = 10**(3*(si_prefix_symbols.index(final_prefix) - si_prefix_symbols.index(initial_prefix)))
        except ValueError:
            raise UndefinedConversionError("Cannot convert {} to {}, unknown SI prefix encountered.".format(initial_unit, final_unit))

    # otherwise only one has a prefix (eg. MHz->Hz or Hz->MHz)
    elif len(initial_unit) < len(final_unit):
        multiplier = si_prefixes.get(final_unit[0])
    else:
        multiplier = si_prefixes.get(initial_unit[0])

    try:
        return float(initial_value) * multiplier
    except TypeError:
        # if an unknown SI prefix is provided then multiplier will be None, hence TypeError
        # FIXME: improve by stating which prefix caused the error
        raise UndefinedConversionError("Cannot convert {} to {}, unknown SI prefix encountered.".format(initial_unit, final_unit))


class UnitConverter(object):
    """ Base class for Unit Conversions. """

    conversions = {}

    def __init__(self):
        pass

    def convert(self, quantity, desired_unit):
        conversion = (parse_quantity(quantity)[1], desired_unit.strip())

        try:
            return conversions[conversion](value)
        except KeyError:
            raise UndefinedConversionError("Conversion from '{}' to '{}' not defined.")
