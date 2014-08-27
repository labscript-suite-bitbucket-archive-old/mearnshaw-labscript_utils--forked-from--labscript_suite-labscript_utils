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

si_prefix_symbols = ('Y','Z','E','P','T','G','M','k','','m',('u',u'µ'),'n','p','f','a','z','y')
si_prefix_multipliers = [10**-x for x in range(-24, 25, 3)]
si_prefixes = dict(zip(si_prefix_symbols, si_prefix_multipliers))

class UndefinedConversionError(Exception):
    pass

def vectorise(method):
    def f(instance, arg):
        # FIXME: many things are iterables including strings, this needs revision
        if iterable(arg):
            return array([method(instance, el) for el in arg])
        else:
            return method(instance, arg)
    return f


def differ_by_order_of_magnitude(unit1, unit2):
    """ Return True if units differ by some SI prefix, otherwise False. """
    
    # identical units differ by 10^0
    if unit1 == unit2:
        return True
    # otherwise test for cases [G]Hz==[M]Hz, [M]Hz==Hz, Hz==[M]Hz
    elif unit1[1:] == unit2[1:]:
        return True
    elif unit1[1:] == unit2:
        return True
    elif unit1 == unit2[1:]:
        return True
    else:
        return False


def parse_quantity(quantity):
    """ Given some quantity parse out the value and unit. eg. "1 MHz" => (1, "MHz") """

    quantity = quantity.strip()
    unit_index = re.search('[A-Z]', quantity, re.IGNORECASE).start()
    return (float(quantity[:unit_index]), quantity[unit_index:])


def magnitude_conversion(quantity, desired_unit):
    """ Change order of magnitude of given quantity.
    
        Examples
        --------
        magnitude_conversion("1.2MHz", "Hz") => 1.2e6
        magnitude_conversion("4 fm", "m") => 4e-15
    """

    quantity, desired_unit = quantity.strip(), desired_unit.strip()

    initial_value, initial_unit = parse_quantity(initial_quantity)

    # if supplied units are the same, no conversion to be done so return value
    if initial_unit == desired_unit:
        return initial_value

    # ensure that units are the same (other than the order of magnitude)
    if not differ_by_order_of_magnitude(initial_unit, desired_unit):
        raise UndefinedConversionError("{} and {} are different units, cannot do order of magnitude conversion".format(initial_unit, desired_unit))

    if len(initial_unit) == len(desired_unit):
        # if they are not the same (already tested) but have equal lengths, both
        # have some prefix (eg. GHz->MHz)
        initial_prefix, final_prefix = initial_unit[0], desired_unit[0]

        # exponent is then 3*distance between these prefixes in the symbol list
        try:
            multiplier = 10**(3*(si_prefix_symbols.index(final_prefix) - si_prefix_symbols.index(initial_prefix)))
        except ValueError:
            raise UndefinedConversionError("Cannot convert {} to {}, unknown SI prefix encountered.".format(initial_unit, desired_unit))

    # otherwise only one has a prefix (eg. MHz->Hz or Hz->MHz)
    elif len(initial_unit) < len(desired_unit):
        multiplier = si_prefixes.get(desired_unit[0])
    else:
        multiplier = si_prefixes.get(initial_unit[0])

    try:
        return initial_value * multiplier
    except TypeError:
        # if an unknown SI prefix is provided then multiplier will be None, hence TypeError
        # FIXME: improve by stating which prefix caused the error
        raise UndefinedConversionError("Cannot convert {} to {}, unknown SI prefix encountered.".format(initial_unit, desired_unit))


def convert(quantity, desired_unit, conversions):
    """ Given some quantity (string containing value and unit), some desired
        unit (string), and a dictionary describing possible conversions (see
        below), return the converted value.

        Parameters
        ----------
        quantity : string
            Value with unit for conversion, eg. "4 MHz"
        desired_unit : string
        conversions : dict
            mappings {('unit1', 'unit2') : function_from_unit1_to_unit2, ...}
    """

    value, unit = parse_quantity(quantity)
    desired_unit = desired_unit.strip()

    if differ_by_order_of_magnitude(unit, desired_unit):
        return order_of_magnitude_conversion(quantity, desired_unit)
    else:
        conversion = (unit, desired_unit)
        try:
            return conversions[conversion](value)
        except KeyError:
            raise UndefinedConversionError("Conversion from {} to {} not defined".format(unit, desired_unit))
