#!/usr/bin/env python
# coding: utf-8

"""
    Module that contains the "dprint" function to help debugging
"""

# =================================================================================================
# GLOBAL PARAMETERS
# =================================================================================================

__author__ = "JL31"
__version__ = "1.0"
__maintainer__ = "JL31"
__date__ = "January 2020"
__all__ = ["dprint"]


# ==================================================================================================
# IMPORTS
# ==================================================================================================

import inspect


# ==================================================================================================
# FUNCTIONS
# ==================================================================================================

# ====================
def dprint(parameter):
    """
        Function that enables to print the name and the value of the input parameter of the function

        Exemple with the standard print function :

        >>> variable_1 = 10.0
        >>> print(variable_1)
        10.0

        Then with the dprint function :

        >>> variable_1 = 10.0
        >>> dprint(variable_1)
        variable_1 : 10.0

        The enabled types for the input parameter of the functions are :
        - None
        - str
        - int
        - float
        - long
        - bool

        :param parameter: parameter whose we want to display the name followed by its value 
        :type parameter: None | str | int | float | long | bool
    """

    # list of the authorized types for the input parameter of the function
    enabled_types_list = ["NoneType", "str", "int", "float", "long", "bool"]

    # stack content retrieval
    stack_content = inspect.stack()

    # calling function name retrieval
    calling_function_name = stack_content[0].function

    # variable type check
    variable_type = type(parameter).__name__

    if variable_type not in enabled_types_list:

        enabled_types_list_tmp = [ "- " + type_ + "\n" for type_ in enabled_types_list ]
        enabled_types_list_str = "".join(enabled_types_list_tmp)

        message = ("The input parameter of the function has a type that is not handled by this function \"{}\" : {}\n"
                   "The possible types are the following ones :\n"
                   "{}").format(calling_function_name,
                                variable_type,
                                enabled_types_list_str)
        raise TypeError(message)

    # variable name retrieval
    variable_name = stack_content[1].code_context

    if variable_name is None:

        variable_name_error = ("--- CONTEXT ERROR ---\n"
                               "\t The input parameter used for the \"dprint\" function does not exist in this context.\n"
                               "\t If you are trying to use the \"dprint\" function in an interpreter the \"code_context\" is None so the function will not run properly.\n"
                               "\t This function has been intended for code debugging purpose in python file but not in interpreter, so please use it adequately :-)\n"
                               "\t If you are not using the function through an interpreter please send your issue (complete exemple with context) to mainteners (see Pypi for email addresses).")
        raise ValueError(variable_name_error)

    variable_name = variable_name[0]
    variable_name = variable_name.strip()
    variable_name = variable_name.split('(')[1].replace(')','')
    
    if "self" in variable_name:

        instance_name = stack_content[2][4][0]
        instance_name = instance_name.strip()
        instance_name = instance_name.split(".")[0]

        # variable name and value display
        print("[ class instance is : \"{}\" ] {} : {}".format(instance_name, variable_name, parameter))

    else:

        # variable name and value display
        print("{} : {}".format(variable_name, parameter))


# ==================================================================================================
# USE
# ==================================================================================================

if __name__ == "__main__":

    pass
