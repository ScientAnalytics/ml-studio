#!/usr/bin/env python3
# =========================================================================== #
#                        SERVICES: VALIDATION: RULES                          #
# =========================================================================== #
# =========================================================================== #
# Project: ML Studio                                                          #
# Version: 0.1.14                                                             #
# File: \rules.py                                                             #
# Python Version: 3.7.3                                                       #
# ---------------                                                             #
# Author: John James                                                          #
# Company: Decision Scients                                                   #
# Email: jjames@decisionscients.com                                           #
# ---------------                                                             #
# Create Date: Friday December 20th 2019, 5:06:57 am                          #
# Last Modified: Friday December 20th 2019, 10:33:23 am                       #
# Modified By: John James (jjames@decisionscients.com)                        #
# ---------------                                                             #
# License: Modified BSD                                                       #
# Copyright (c) 2019 Decision Scients                                         #
# =========================================================================== #
"""Module contains the validation rules.

This module implements the strategy design pattern with a fluent interface,
and includes:

    Syntactic Rules
    ------------------
    * NoneRule : NoneRule, which evaluates whether the value of a specific 
        property is equal to None.
    * NotNoneRule : NotNoneRule, which evaluates whether the value of a 
        specific property is not equal to None.
    * EmptyRule : EmptyRule, which evaluates whether the value of a 
        specific property is empty.
    * NotEmptyRule : NotEmptyRule, which evaluates whether the value 
        of a specific property is not empty.        
    * BoolRule : BoolRule, which evaluates whether the value of a 
        specific property is Boolean.
    * IntegerRule : IntegerRule, which evaluates whether the value of a specific 
        property is an integer.
    * FloatRule : FloatRule, which evaluates whether the value of a 
        specific property is an float.
    * NumberRule : NumberRule, which evaluates whether the value of a 
        specific property is an a number.
    * StringRule : StringRule, which evaluates whether the value of a 
        specific property is a string.

    Semantic Rules
    -----------------
    * EqualRule : EqualRule, which ensures that the value of a specific property    
        is equal to a particular value  or that of another instance 
        and/or property.  
    * NotEqualRule : NotEqualRule, which ensures that the value of a specific 
        property is not equal to a particular value or that of another instance 
        and/or property.                
    * AllowedRule : AllowedRule, which ensures the value of a specific property 
        is one of a discrete set of allowed values. 
    * DisAllowedRule : EqualRule, which ensures the value of a specific property 
        is none of a discrete set of disallowed values.     
    * LessRule : LessRule, which ensures the value of a specific property is 
        less than a particular  value or that of another instance and / or 
        property. If the inclusive parameter is True, this evaluates
        less than or equal to.
    * GreaterRule : GreaterRule, which ensures the value of a specific property 
        is greater than a particulcar value or greater than the value of 
        another property. If the inclusive parameter is True, this evaluates
        greater than or equal to.
    * BetweenRule : BetweenRule, which ensures the value of a specific property 
        is between than a particulcar value or greater than the value of 
        another property. If the inclusive parameter is True, the range is 
        evaluated as inclusive.
    * RegexRule : EqualRule, which ensures the 
        value of a specific property matches the given regular expression(s).    

    Rule Sets
    ---------
    * RuleSet : Composite of rules along with a logical operand that specifies
        how the RuleSet must be evaluated.

"""
#%%
from abc import ABC, abstractmethod, abstractproperty
import builtins
from collections import defaultdict
from collections.abc import Iterable
from dateutil.parser import parse
from datetime import datetime
import getpass
import math
import numbers
import operator
import os
import re
import sys
import time
from uuid import uuid4

import numpy as np
import pandas as pd

from ml_studio.services.validation.conditions import Condition, SyntacticCondition
from ml_studio.services.validation.conditions import SemanticCondition
from ml_studio.services.validation.conditions import IsNone, IsEmpty, IsBool
from ml_studio.services.validation.conditions import IsInt, IsFloat
from ml_studio.services.validation.conditions import IsNumber, IsString
from ml_studio.services.validation.conditions import IsEqual, IsIn, IsLess
from ml_studio.services.validation.conditions import IsGreater, IsMatch
from ml_studio.utils.data_operations import is_array, is_simple_array
from ml_studio.utils.data_operations import is_homogeneous_array
from ml_studio.utils.data_operations import is_numpy_convertable
from ml_studio.utils.data_operations import to_native_type
from ml_studio.utils.data_operations import coerce_homogeneous_array
from ml_studio.utils.misc import format_text

# --------------------------------------------------------------------------- #
#                                   RULE                                      #  
# --------------------------------------------------------------------------- #
class Rule(ABC):
    """Base class for all rules."""

    def __init__(self, instance, target_name, parentname, array_ok=False, **kwargs):

        # Designate unique/opaque userid and other metadata        
        self._id = uuid4()
        self._created = datetime.now()
        self._user = getpass.getuser()

        # Class and attribute to which this rule applies
        self._instance = instance
        self._target_name = target_name
        self._parent_name = parentname

        # Conditions
        self._conditions = defaultdict(set)

        # Rule properties 
        self._array_ok = array_ok
        self._is_valid = True
        self._invalid_messages = []
        self._invalid_values = []

    # ----------------------------------------------------------------------- #
    #                               Properties                                #
    # ----------------------------------------------------------------------- #
    @property
    def array_ok(self):
        return self._array_ok

    @array_ok.setter
    def array_ok(self, value):
        if isinstance(value, bool):
            self._array_ok = value
        else:
            raise TypeError("array_ok property requires a Boolean value.")

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def invalid_messages(self):
        return self._invalid_values

    # ----------------------------------------------------------------------- #
    #                               Conditions                                #
    # ----------------------------------------------------------------------- #
    def when(self, condition):
        """Adds a single condition that must be met for a rule to apply."""        
        if isinstance(condition, Condition):
            self._conditions['when'] = condition
        else:
            raise TypeError("condition must be of type Condition.")
        return self

    def when_all(self, conditions):
        """Adds a list of rules, all of which must be met for a rule to apply."""
        if is_array(conditions):
            self._conditions['when_all'] = conditions
        else:
            raise TypeError("conditions must be an array-like object \
                containing Condition objects.")
        return self

    def when_any(self, conditions):
        """Adds a list of rules, all of which must be met for a rule to apply."""        
        if is_array(conditions):
            self._conditions['when_any'] = conditions
        else:
            raise TypeError("conditions must be an array-like object \
                containing Condition objects.")
        return self

    def _evaluate_when(self):
        condition = self._conditions.get('when')
        if condition is not None:
            return condition()
        else:
            return True

    def _evaluate_when_all(self):
        if self._conditions.get('when_all'):
            results = []
            for condition in self._conditions.get('when_all'):
                results.append(condition())
            return all(results)
        else:
            return True

    def _evaluate_when_any(self):
        if self._conditions.get('when_any'):
            results = []
            for condition in self._conditions.get('when_any'):
                results.append(condition())
            return any(results)
        else:
            return True

    def _evaluate_conditions(self):
        """Evaluates 'when', 'when_all', and 'when_any' conditions."""
        return self._evaluate_when() and self._evaluate_when_all() and \
            self._evaluate_when_any()

    # ----------------------------------------------------------------------- #
    #                     Validate Parameters and Compile                     #
    # ----------------------------------------------------------------------- #
    def _validate_params(self, value):
        # Ensure the instance class and attribute_name are a match.
        if not hasattr(self._instance, self._target_name):
            raise AttributeError("{targetname} is not a valid attribute on the\
                {parentname} class.".format(
                    targetname=self._target_name,
                    parentname=self._parent_name
                ))
        
        
        # Raise error if arrays encountered and arrays_ok = False
        if not self._array_ok:
            if is_array(value):
                raise TypeError("Arrays are not permitted for the {parentname}\
                    class {targetname} property.".format(
                        parentname = self._parent_name,
                        targetname = self._target_name
                    ))                    

    def compile(self):
        self._is_valid = True
        self._invalid_values = []
        self._invalid_messages = []        
        
        if self._conditions:
            if self._conditions.get('when'):
                self._conditions['when'].compile()
            if self._conditions.get('when_any'):
                for idx, condition in enumerate(self._conditions['when_any']):
                    condition.compile()
                    self._conditions['when_any'][idx] = condition
            if self._conditions.get('when_all'):
                for idx, condition in enumerate(self._conditions['when_all']):
                    condition.compile()
                    self._conditions['when_all'][idx] = condition                

    # ----------------------------------------------------------------------- #
    #                         Validation Methods                              #
    # ----------------------------------------------------------------------- #
    @abstractmethod
    def _get_evaluation_function(self, value):
        pass

    @abstractmethod
    def _coerce(self, value, kind=None, force_numeric=False):
        pass

    def validate(self, value, coerced=False):       
        self._validate_params(value)
        self.compile()  

        # evaluate conditions evaluates to True if all conditions are met.
        if self._evaluate_conditions():

            # Get evaluation function that will be used to evaluate an attribute
            is_invalid = self._get_evaluation_function(value)

            # Create inner function to recurse through array-like structures.
            def validate_recursive(value, is_invalid):

                # If array, initiate a recursive call for each array element.
                if is_array(value):
                    [validate_recursive(v, is_invalid) for v in value]
                elif is_invalid(value):
                    self._invalid_values.append(value)

            validate_recursive(value, is_invalid)

            # Save results of the evaluation
            self._validated_value = value
            self._invalid_messages.append(self._error_message())                
            if self._invalid_values:
                self._is_valid = False
            else:
                self._is_valid = True 

            # if invalid and data has not been coerced, try coercing the data
            # and reevaluate.
            if not self._is_valid and not coerced:
                coerced, self._validated_value = self._coerce(value)
                if coerced:
                    self.validate(self._validated_value, coerced)

        else:
            self._validated_value = value
            self._is_valid = True
            
    # ----------------------------------------------------------------------- #
    #                         Printing and Messaging                          #
    # ----------------------------------------------------------------------- #
    @abstractmethod
    def _error_message(self):
        pass

    def _print_context(self, context):
        text = "    {context}:".format(
            context=context
        )
        print(text)

    def _print_condition(self, condition):
        if isinstance(condition, SyntacticCondition):
            text = "      {a} {condition}".format(
                        a = condition.a,
                        condition=condition.__class__.__name__
                    )
        elif isinstance(condition, SemanticCondition):
            text = "      {a} {condition} {b}".format(
                a=condition.a,
                condition=condition.__class__.__name__,
                b=condition.b
            )        
        print(text)

    def _print_conditions(self, conditions):
        for condition in conditions:
            self._print_condition(condition)

    def _print_rule(self):

        rule_text = "\n  {rulename}:".format(
            rulename = self.__class__.__name__
        )
        print(rule_text)
        if self._conditions:
            if self._conditions.get('when'):
                condition = self._conditions.get('when')
                self._print_context(context='when')
                self._print_condition(condition=condition)
            if self._conditions.get('when_any'):
                conditions = self._conditions.get('when_any')                
                self._print_context(context='when any')
                self._print_conditions(conditions)
            if self._conditions.get('when_all'):
                conditions = self._conditions.get('when_all')                
                self._print_context(context='when all')
                self._print_conditions(conditions)

    def print_rule(self):
        self.compile()
        self._print_rule()

    def raise_invalid_val(self):
        messages = [m for m in self._invalid_messages]
        raise ValueError(messages)

# --------------------------------------------------------------------------- #
#                               RULESET                                       #  
# --------------------------------------------------------------------------- #       
class RuleSet:
    """Composite of rules with a logical operator defining rules of evaluation.
    
    A RuleSet is comprised of a set of rules and a logical operator which
    specifies how the rules should be evaluated as a group. 

    Parameters
    ----------
    operator : str. 'or' or 'and'.
        The logical operator to be used when evaluating the RuleSet

    rules : A list of Rule objects
        Rules to be evaluated

    Raises
    ------
    ValueError if operator is not in ['or', 'and']
    
    """  

    def __init__(self, operator='or', rules=None):
        if rules is None:
            self._rules = []
        else:
            self._rules = rules
        self._operator = operator
        self._is_valid = True
        self._invalid_messages = []

    @property
    def operator(self):
        return self._operator

    @operator.setter
    def operator(self, value):
        if value in ['or', 'and']:
            self._operator = value
        else:
            raise ValueError("{operator} is an invalid operator. Valid \
                operators are ['or', 'and']".format(
                    operator=value
                ))

    @property
    def is_valid(self):
        return self._is_valid

    def add_rule(self, rule):
        self._rules.append(rule)

    def del_rule(self, rule):
        self._rules.remove(rule)

    def validate(self, value, **kwargs):
        results = []        
        for rule in self._rules:
            rule.validate(value)
            results.append(rule.is_valid)
            if not rule.is_valid:
                self._invalid_messages.append(rule.invalid_messages)
        if self._operator == 'or':
            self._is_valid = any(results)
        else:
            self._is_valid = all(results)

    def compile(self):
        if self._rules:
            for idx, rule in enumerate(self._rules):
                rule.compile()
                self._rules[idx] = rule

    def print_rule(self):        
        if self._operator == 'or':
            operator_text = 'passes validation if any of the following rules pass.'
        else:
            operator_text = 'passes validation if all of the following rules pass.'
        if self._rules:
            text = "\n {ruleset} {operatortext}".format(
                ruleset = self.__class__.__name__,
                operatortext=operator_text
            )
            print(text)
            for rule in self._rules:
                rule.print_rule()

    def raise_invalid_val(self):
        messages = [m for m in self._invalid_messages]
        raise ValueError(messages)

# --------------------------------------------------------------------------- #
#                              SYNTACTICRULE                                  #  
# --------------------------------------------------------------------------- #      
class SyntacticRule(Rule):
    """Abstract base class for syntactic rules."""
    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(SyntacticRule, self).__init__(instance=instance,
                                            attribute_name=attribute_name,
                                            array_ok=array_ok,
                                            **kwargs)

# --------------------------------------------------------------------------- #
#                                NONERULE                                     #  
# --------------------------------------------------------------------------- #            
class NoneRule(SyntacticRule):
    """Evaluates whether the value of a specific property is None."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(NoneRule, self).__init__(instance=instance,
                                       attribute_name=attribute_name,
                                       array_ok=array_ok,
                                       **kwargs)
    
    def _coerce(self, value, kind=None, force_numeric=False):
        """Coerce an attribute to an appropriate value/type if possible."""
        if value in ["None", "none"]:
            value = None
            coerced = True
        else:
            value = value
            coerced = False

        return coerced, value

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return value is not None

        return is_invalid
   
    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is not None. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                value=self._invalid_values.copy())
        
        formatted_msg = format_text(msg)
        return formatted_msg

# --------------------------------------------------------------------------- #
#                                NotNoneRULE                                  #  
# --------------------------------------------------------------------------- #            
class NotNoneRule(SyntacticRule):
    """Evaluates whether the value of a specific property is not None."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(NotNoneRule, self).__init__(instance=instance,
                                       attribute_name=attribute_name,
                                       array_ok=array_ok,
                                       **kwargs)

    def _coerce(self, value, kind=None, force_numeric=False):
        """Coerce an attribute to an appropriate value/type if possible."""
        if value in ["None", "none"]:
            value = None
            coerced = True
        else:
            value = value
            coerced = False

        return coerced, value

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return value is None

        return is_invalid

    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class has values \
            that are None".format(
                attribute=self._target_name,
                parentname=self._parent_name)
        
        formatted_msg = format_text(msg)
        return formatted_msg



# --------------------------------------------------------------------------- #
#                                EmptyRULE                                    #  
# --------------------------------------------------------------------------- #            
class EmptyRule(SyntacticRule):
    """Evaluates whether the value of a specific property is Empty."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(EmptyRule, self).__init__(instance=instance,
                                       attribute_name=attribute_name,
                                       array_ok=array_ok,
                                       **kwargs)

    def _coerce(self, value, kind=None, force_numeric=False):
        """Coerce an attribute to an appropriate value/type if possible."""
        # No coercion for this class.
        value = value
        coerced = False
        return coerced, value

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return not IsEmpty(value)()

        return is_invalid
        
    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is not empty. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                value=self._invalid_values.copy())
        
        formatted_msg = format_text(msg)
        return formatted_msg

# --------------------------------------------------------------------------- #
#                                NotEmptyRULE                                 #  
# --------------------------------------------------------------------------- #            
class NotEmptyRule(SyntacticRule):
    """Evaluates whether the value of a specific property is Empty."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(NotEmptyRule, self).__init__(instance=instance,
                                       attribute_name=attribute_name,
                                       array_ok=array_ok,
                                       **kwargs)

    def _coerce(self, value, kind=None, force_numeric=False):
        """Coerce an attribute to an appropriate value/type if possible."""
        # No coercion for this class.
        value = value
        coerced = False
        return coerced, value

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return IsEmpty(value)()

        return is_invalid

        
    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is \
            empty.".format(
                attribute=self._target_name,
                parentname=self._parent_name)
        
        formatted_msg = format_text(msg)
        return formatted_msg

# --------------------------------------------------------------------------- #
#                                 BoolRULE                                    #  
# --------------------------------------------------------------------------- #            
class BoolRule(SyntacticRule):
    """Evaluates whether the value of a specific property is a Boolean."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(BoolRule, self).__init__(instance=instance,
                                           attribute_name=attribute_name,
                                           array_ok=array_ok,
                                           **kwargs)

    def _coerce(self, value, kind=None, force_numeric=False):
        """Attempt to coerce the property to a valid boolean."""        
        true_list = ['True', 'true', 'yes','y', '1']
        false_list = ['False', 'false', 'no', 'n', '0']

        coerced = False

        # Handle value as a string
        if isinstance(value, str):
            if value in true_list:
                value = True
                coerced = True
            elif value in false_list:
                value = False
                coerced = True
        # Handle value as a number
        elif isinstance(value, (int, float)):
            if value == 0:
                value = False
                coerced = True
            else:
                value = True
                coerced = True
        # Handle array-like
        elif is_array(value):
            value = [x if x not in true_list else True for x in value]            
            value = [x if x not in false_list else False for x in value]
            value = [True if isinstance(x, (int, float)) and x == 0 else x for x in value]             
            value = [False if isinstance(x, (int, float)) and x > 0 else x for x in value]             
            coerced = True

        return coerced, value

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return not (isinstance(value, bool) or isinstance(value, np.bool_))

        return is_invalid
        
    def _error_message(self):
        msg = "The {attribute} property of the {parentname} has non-Boolean \
            values. Invalid value(s): '{value}'".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                value=self._invalid_values.copy())
        
        formatted_msg = format_text(msg)
        return formatted_msg

# --------------------------------------------------------------------------- #
#                                 IntegerRule                                 #  
# --------------------------------------------------------------------------- #            
class IntegerRule(SyntacticRule):
    """Evaluates whether the value of a specific property is an integer."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(IntegerRule, self).__init__(instance=instance,
                                           attribute_name=attribute_name,
                                           array_ok=array_ok,
                                           **kwargs)

    def _coerce(self, value, kind=("i", "u"), force_numeric=False):
        """Attempt to coerce the property to a valid integer."""        

        coerced = False
        if is_array(value):
            try:
                value = coerce_homogeneous_array(value, kind=kind, 
                    force_numeric=force_numeric)       
            except ValueError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                raise ValueError("ValueError occurred in IntegerRule class, \
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except TypeError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                raise TypeError("TypeError occurred in IntegerRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except OverflowError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("OverflowError occurred in IntegerRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))                               
            else:
                coerced = True

        return coerced, value 

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return not isinstance(value, int)

        return is_invalid


    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class has values \
            that are not integers. Invalid value(s): '{value}'".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                value=self._invalid_values.copy())
        
        formatted_msg = format_text(msg)
        return formatted_msg


# --------------------------------------------------------------------------- #
#                                FloatRULE                                    #  
# --------------------------------------------------------------------------- #            
class FloatRule(SyntacticRule):
    """Evaluates whether the value of a specific property is a float."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(FloatRule, self).__init__(instance=instance,
                                           attribute_name=attribute_name,
                                           array_ok=array_ok,
                                           **kwargs)

    def _coerce(self, value, kind=("f"), force_numeric=False):
        """Attempt to coerce the property to a valid numeric."""        
        coerced = False

        if is_array(value):
            try:
                value = coerce_homogeneous_array(value, kind=kind,
                            force_numeric=force_numeric)
            except ValueError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("ValueError occurred in FloatRule class, \
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except TypeError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("TypeError occurred in FloatRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except OverflowError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("OverflowError occurred in FloatRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))                               
            else:
                coerced = True

        return coerced, value 

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return not isinstance(value, float)

        return is_invalid

    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class has values \
            that are not floats. Invalid value(s): '{value}'".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                value=self._invalid_values.copy())
        
        formatted_msg = format_text(msg)
        return formatted_msg

# --------------------------------------------------------------------------- #
#                                NumberRULE                                   #  
# --------------------------------------------------------------------------- #            
class NumberRule(SyntacticRule):
    """Evaluates whether the value of a specific property is a number."""

    def __init__(self, instance, attribute_name, array_ok=False, **kwargs):
        super(NumberRule, self).__init__(instance=instance,
                                           attribute_name=attribute_name,
                                           array_ok=array_ok,
                                           **kwargs)

    def _coerce(self, value, kind=None, force_numeric=False):
        """Attempt to coerce the property to a valid numeric."""        
        coerced = False

        if is_array(value):

            try:
                value = coerce_homogeneous_array(value, kind=kind,
                            force_numeric=force_numeric)
            except ValueError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("ValueError occurred in NumberRule class, \
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except TypeError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("TypeError occurred in NumberRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except OverflowError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("OverflowError occurred in NumberRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))                               
            else:
                coerced = True

        return coerced, value 
        
    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return not isinstance(value, (int, float))

        return is_invalid


    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class has values \
            that are not numbers. Invalid value(s): '{value}'".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                value=self._invalid_values.copy())
        
        formatted_msg = format_text(msg)
        return formatted_msg

# --------------------------------------------------------------------------- #
#                                StringRULE                                   #  
# --------------------------------------------------------------------------- #            
class StringRule(SyntacticRule):
    """Evaluates whether the value of a specific property is a string."""

    def __init__(self, instance, attribute_name, array_ok=False, 
                 blanks_ok=False, **kwargs):
        super(StringRule, self).__init__(instance=instance,
                                           attribute_name=attribute_name,
                                           array_ok=array_ok,
                                           **kwargs)
        self.blanks_ok = blanks_ok

    def _coerce(self, value, kind=("S","U"), force_numeric=False):
        """Attempt to coerce the property to a valid numeric."""        
        coerced = False

        if is_homogeneous_array(value):

            try:
                value = coerce_homogeneous_array(value, kind=kind,
                            force_numeric=force_numeric)
            except ValueError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("ValueError occurred in StringRule class, \
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except TypeError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("TypeError occurred in StringRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))         
            except OverflowError as e:
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("OverflowError occurred in StringRule class. {e}\
                    line {line}. {e}\
                    Value(s) received: {value}".format(
                        e=e,
                        value=value,
                        line=line
                    ))                               
            else:
                coerced = True    

        else:
            value = str(value)
            coerced = True

        return coerced, value 

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the NoneRule class."""
            return not isinstance(value, str)

        return is_invalid


    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class has values \
            that are not strings. Invalid value(s): '{value}'".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                value=self._invalid_values.copy())
        
        formatted_msg = format_text(msg)
        return formatted_msg


# --------------------------------------------------------------------------- #
#                                SEMANTICRULE                                 #  
# --------------------------------------------------------------------------- #                    
class SemanticRule(SyntacticRule):
    """Abstract base class for rules requiring cross-reference to other objects.

    This class introduces the instance and attribute name for an reference
    value in the constructor. Another method is exposed to obtain the value
    from the reference object. 
    
    Parameters
    ----------
    value : Any
        The validated value must be equal to this value.

    instance : ML Studio object
        The instance of a class containing the equality value

    attribute_name : str
        The name of the attribute containing the equality value 

    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, **kwargs):
        super(SemanticRule, self).__init__(instance=instance,
                                           attribute_name=attribute_name,
                                           array_ok=array_ok,
                                           **kwargs)        
        # Note reference value may be any python type. If it is a dict,
        # it is assumed to have two elements: an instance containing the
        # reference value for the rule and the attribute_name for the
        # reference value.
        self._reference_value = reference_value

    def _validate_params(self, value):
        super(SemanticRule, self)._validate_params(value=value)

        # Add functionality to validate reference 
        if isinstance(self._reference_value, dict):
            if not self._reference_value.get('instance'):
                raise KeyError("If self._reference is a dictionary, it must\
                    have an 'instance' key and associated value. This \
                    instance should contain the reference value.")

            if not self._reference_value.get('attribute_name'):
                raise KeyError("If self._reference is a dictionary, it must\
                    have an 'attribute_name' key and associated value. This \
                        attribute should contain the reference value.")
        
    def compile(self):
        super(SemanticRule, self).compile()
        # Extract instance and attribute_name from reference value if 
        # it is a dictionary.
        if isinstance(self._reference_value, dict):
            instance = self._reference_value.get('instance')
            attribute_name = self._reference_value.get('attribute_name')
            self._reference_value = getattr(instance, attribute_name)    

    def _coerce(self, value, kind=None, force_numeric=False):
        """Attempt to coerce the property to an appropriate value/type."""        
        coerced = False
        value = value
        return coerced, value    

# --------------------------------------------------------------------------- #
#                                 EQUALRULE                                   #  
# --------------------------------------------------------------------------- #            
class EqualRule(SemanticRule):
    """Evaluates equality of a property vis-a-vis another value or property.
    
    The EqualRule applies to basic types as well as array-like objects. Array-
    like objects are evaluated against basic types by recursing over each 
    element of the array. When evaluating two array-like objects, equality
    is evaluated element-wise using numpy array-equal.

    Parameters
    ----------
    value : Any
        The validated value must be equal to this value.

    instance : ML Studio object
        The instance of a class containing the equality value

    attribute_name : str
        The name of the attribute containing the equality value 
    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, **kwargs):
        super(EqualRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)        


    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the EqualRule class."""
            # Handle value and reference value arrays
            if is_array(value) and is_array(self._reference_value):
                attribute_value = np.array(value)
                reference_value = np.array(self._reference_value)
                return not (np.array_equal(attribute_value, reference_value))
            # Handle objects of different lengths.
            elif not is_array(value) and is_array(self._reference_value):
                return True
            # Handle array and reference value as basic type
            else:
                return(value != self._reference_value)            

        return is_invalid
            

    def validate(self, value, coerced=False):       
        self._validate_params(value)
        self.compile()  

        # evaluate conditions evaluates to True if all conditions are met.
        if self._evaluate_conditions():

            # Get evaluation function that will be used to evaluate an attribute
            is_invalid = self._get_evaluation_function(value)

            if is_invalid(value):
                self._invalid_values.append(value)

            # Save results of the evaluation
            self._validated_value = value
            self._invalid_messages.append(self._error_message())                
            if self._invalid_values:
                self._is_valid = False
            else:
                self._is_valid = True 

            # if invalid and data has not been coerced, try coercing the data
            # and reevaluate.
            if not self._is_valid and not coerced:
                coerced, self._validated_value = self._coerce(value)
                if coerced:
                    self.validate(self._validated_value, coerced)

        else:
            self._validated_value = value
            self._is_valid = True

    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is not equal \
            to {refval}. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                refval = self._reference_value,
                value=self._invalid_values.copy())                    
        
        formatted_msg = format_text(msg)
        return formatted_msg 

# --------------------------------------------------------------------------- #
#                              NOTEQUALRULE                                   #  
# --------------------------------------------------------------------------- #            
class NotEqualRule(SemanticRule):
    """Evaluates equality of a property vis-a-vis another value or property.
    
    The NotEqualRule applies to basic types as well as array-like objects. Array-
    like objects are evaluated against basic types by recursing over each 
    element of the array. When evaluating two array-like objects, equality
    is evaluated element-wise using numpy array-equal.

    Parameters
    ----------
    value : Any
        The validated value must be equal to this value.

    instance : ML Studio object
        The instance of a class containing the equality value

    attribute_name : str
        The name of the attribute containing the equality value 
    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, **kwargs):
        super(NotEqualRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)   

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the EqualRule class."""
            # Handle value and reference value arrays
            if is_array(value) and is_array(self._reference_value):
                attribute_value = np.array(value)
                reference_value = np.array(self._reference_value)
                return np.array_equal(attribute_value, reference_value)
            # Handle objects of different lengths.
            elif not is_array(value) and is_array(self._reference_value):
                return False
            # Handle array and reference value as basic type
            else:
                return(value == self._reference_value)  

        return is_invalid
            

    def validate(self, value, coerced=False):       
        self._validate_params(value)
        self.compile()  

        # evaluate conditions evaluates to True if all conditions are met.
        if self._evaluate_conditions():

            # Get evaluation function that will be used to evaluate an attribute
            is_invalid = self._get_evaluation_function(value)

            if is_invalid(value):
                self._invalid_values.append(value)

            # Save results of the evaluation
            self._validated_value = value
            self._invalid_messages.append(self._error_message())                
            if self._invalid_values:
                self._is_valid = False
            else:
                self._is_valid = True 

            # if invalid and data has not been coerced, try coercing the data
            # and reevaluate.
            if not self._is_valid and not coerced:
                coerced, self._validated_value = self._coerce(value)
                if coerced:
                    self.validate(self._validated_value, coerced)

        else:
            self._validated_value = value
            self._is_valid = True
  

    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is equal \
            to {refval}. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                refval = self._reference_value,
                value=self._invalid_values.copy())                    
        
        formatted_msg = format_text(msg)
        return formatted_msg 

# --------------------------------------------------------------------------- #
#                                ALLOWEDRULE                                  #  
# --------------------------------------------------------------------------- #            
class AllowedRule(SemanticRule):
    """Evaluates whether the value or values of a property is/are allowed.

    The evaluated property is confirmed to be one of a set of allowed values. 
    If the evaluated property is an array-like, its values are recursively
    evaluated against the allowed values.
    
    Parameters
    ----------
    value : Any
        The allowed values.

    instance : ML Studio object
        The instance of a class containing the allowed values.

    attribute_name : str
        The name of the attribute containing the allowed values.
    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, **kwargs):
        super(AllowedRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)   

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the EqualRule class."""
            # Convert to numpy arrays for convenient evaluation                         
            reference_value = np.array(self._reference_value)
            return value not in reference_value

        return is_invalid
            

    def _error_message(self):
        msg = "The value of {attribute} property of the {parentname} class is \
            not allowed. Allowed value(s): '{allowed}' \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                allowed = self._reference_value,
                value=self._invalid_values.copy())

        formatted_msg = format_text(msg)
        return formatted_msg 


# --------------------------------------------------------------------------- #
#                                DISALLOWEDRULE                               #  
# --------------------------------------------------------------------------- #            
class DisAllowedRule(SemanticRule):
    """Evaluates whether the value or values of a property is/are disallowed.

    The evaluated property is confirmed not to be one of a set of disallowed 
    values. If the evaluated property is an array-like, its values are recursively
    evaluated against the disallowed values.
    
    Parameters
    ----------
    value : Any
        The disallowed values.

    instance : ML Studio object
        The instance of a class containing the disallowed values.

    attribute_name : str
        The name of the attribute containing the disallowed values.
    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, **kwargs):
        super(DisAllowedRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)   

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the EqualRule class."""
            # Convert to numpy arrays for convenient evaluation                         
            reference_value = np.array(self._reference_value)
            return value in reference_value

        return is_invalid


    def _error_message(self):
        msg = "The value of {attribute} property of the {parentname} class is \
            not allowed. Allowed value(s): '{allowed}' \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                allowed = self._reference_value,
                value=self._invalid_values.copy())

        formatted_msg = format_text(msg)
        return formatted_msg 


# --------------------------------------------------------------------------- #
#                                 LESSRULE                                    #  
# --------------------------------------------------------------------------- #            
class LessRule(SemanticRule):
    """Evaluates whether a property is less than another value or property.
    
    The LessRule applies to basic types as well as array-like objects. Array-
    like objects are evaluated against basic types by recursing over each 
    element of the array. When evaluating two array-like objects, the LessRule
    is evaluated element-wise using numpy array-less.

    Parameters
    ----------
    value : Any
        The validated value must be less to this value.

    instance : ML Studio object
        The instance of a class containing the lessity value

    attribute_name : str
        The name of the attribute containing the lessity value 

    inclusive : bool
        If True, LessRule evaluates less than or equal. Otherwise it 
        evaluates less than exclusively.
    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, inclusive=True, **kwargs):
        super(LessRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)   
        self._inclusive = inclusive

    def _validate_params(self, value):
        super(LessRule, self)._validate_params(value=value)
        if is_array(self._reference_value) and not \
            is_array(value):
            raise ValueError("the 'value' parameter can be an array-like, only \
                when the evaluated attribute value is an array-like.")

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the EqualRule class."""
            # Handle value and reference value arrays
            if is_array(value) and is_array(self._reference_value):
                attribute_value = np.array(value)
                reference_value = np.array(self._reference_value)
                if self._inclusive:
                    return not all(np.less_equal(attribute_value, reference_value))
                else:
                    return not all(np.less(attribute_value, reference_value))
            # Handle objects of different lengths.
            elif not is_array(value) and is_array(self._reference_value):
                if self._inclusive:
                    return not (value <= all(self._reference_value))
                else:
                    return not (value < all(self._reference_value))
            # Handle value array and reference value as basic type
            elif is_array(value) and not is_array(self._reference_value):
                if self._inclusive:
                    return not (all(value) <= self._reference_value)
                else:
                    return not (all(value) < self._reference_value)
            # Handle values as basic types
            else:
                if self._inclusive:
                    return not (value <= self._reference_value)
                else:
                    return not (value < self._reference_value)

        return is_invalid                

    def validate(self, value, coerced=False):       
        self._validate_params(value)
        self.compile()  

        # evaluate conditions evaluates to True if all conditions are met.
        if self._evaluate_conditions():

            # Get evaluation function that will be used to evaluate an attribute
            is_invalid = self._get_evaluation_function(value)

            if is_invalid(value):
                self._invalid_values.append(value)

            # Save results of the evaluation
            self._validated_value = value
            self._invalid_messages.append(self._error_message())                
            if self._invalid_values:
                self._is_valid = False
            else:
                self._is_valid = True 

            # if invalid and data has not been coerced, try coercing the data
            # and reevaluate.
            if not self._is_valid and not coerced:
                coerced, self._validated_value = self._coerce(value)
                if coerced:
                    self.validate(self._validated_value, coerced)

        else:
            self._validated_value = value
            self._is_valid = True
        

    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is not less \
            to {referenceval}. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                referenceval = self._reference_value,
                value=self._invalid_values.copy())                    
        
        formatted_msg = format_text(msg)
        return formatted_msg 

# --------------------------------------------------------------------------- #
#                               GREATERRULE                                   #  
# --------------------------------------------------------------------------- #            
class GreaterRule(SemanticRule):
    """Evaluates whether a property is greater than another value or property.
    
    The GreaterRule applies to basic types as well as array-like objects. Array-
    like objects are evaluated against basic types by recursing over each 
    element of the array. When evaluating two array-like objects, the GreaterRule
    is evaluated element-wise using numpy array-greater.

    Parameters
    ----------
    value : Any
        The validated value must be greater to this value.

    instance : ML Studio object
        The instance of a class containing the greaterity value

    attribute_name : str
        The name of the attribute containing the greaterity value 

    inclusive : bool
        If True, GreaterRule evaluates greater than or equal. Otherwise it 
        evaluates greater than exclusively.
    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, inclusive=True, **kwargs):
        super(GreaterRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)   
        self._inclusive = inclusive

    def _validate_params(self, value):
        super(GreaterRule, self)._validate_params(value=value)
        if is_array(self._reference_value) and not \
            is_array(value):
            raise ValueError("the 'value' parameter can be an array-like, only \
                when the evaluated attribute value is an array-like.")

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
                """Evaluation function for the EqualRule class."""
                # Deal with arrays
                if is_array(value) and is_array(self._reference_value):
                    # Convert value and reference value to numpy arrays
                    attribute_value = np.array(value)                         
                    reference_value = np.array(self._reference_value)
                    if self._inclusive:
                        return not any(np.greater_equal(attribute_value, reference_value))
                    else:
                        return not any(np.greater(attribute_value, reference_value))
                # Handle value array and reference_value a basic type
                elif is_array(value) and not is_array(self._reference_value):
                    if self._inclusive:
                        return not all([v for v in value if v >= self._reference_value])
                    else:
                        return not all([v for v in value if v > self._reference_value])
                # Handle value as basic type and reference_value as array
                elif not is_array(value) and is_array(self._reference_value):
                    if self._inclusive:
                        return not (value >= all(self._reference_value))
                    else:
                        return not (value > all(self._reference_value))
                # Handle value and reference value as basic types
                else:
                    if self._inclusive:
                        return not (value >= self._reference_value)
                    else:
                        return not (value > self._reference_value)

        return is_invalid                

    def validate(self, value, coerced=False):       
        self._validate_params(value)
        self.compile()  

        # evaluate conditions evaluates to True if all conditions are met.
        if self._evaluate_conditions():

            # Get evaluation function that will be used to evaluate an attribute
            is_invalid = self._get_evaluation_function(value)

            if is_invalid(value):
                self._invalid_values.append(value)

            # Save results of the evaluation
            self._validated_value = value
            self._invalid_messages.append(self._error_message())                
            if self._invalid_values:
                self._is_valid = False
            else:
                self._is_valid = True 

            # if invalid and data has not been coerced, try coercing the data
            # and reevaluate.
            if not self._is_valid and not coerced:
                coerced, self._validated_value = self._coerce(value)
                if coerced:
                    self.validate(self._validated_value, coerced)

        else:
            self._validated_value = value
            self._is_valid = True
      

    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is not greater \
            to {referenceval}. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                referenceval = self._reference_value,
                value=self._invalid_values.copy())                    
        
        formatted_msg = format_text(msg)
        return formatted_msg 

# --------------------------------------------------------------------------- #
#                               REGEXRULE                                     #  
# --------------------------------------------------------------------------- #            
class RegexRule(SemanticRule):
    """Evaluates whether a property is regex than another value or property.
    
    The RegexRule validates basic types and array-like objects against a
    regex string pattern. 

    Parameters
    ----------
    value : Any
        The validated value must be regex to this value.

    instance : ML Studio object
        The instance of a class containing the regexity value

    attribute_name : str
        The name of the attribute containing the regexity value 
    """

    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, **kwargs):
        super(RegexRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)   
        
    def _validate_params(self, value):
        super(RegexRule, self)._validate_params(value=value)

        # Raise exception if reference value is not a valid regex string.
        re.compile(self._reference_value)

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
                """Evaluation function for the RegexRule class."""                
                matches = re.search(self._reference_value, value)
                return not matches

        return is_invalid            

    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class does not  \
            match regex pattern {referenceval}. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                referenceval=self._reference_value,
                value=self._invalid_values.copy())

        formatted_msg = format_text(msg)
        return formatted_msg 

class BetweenRule(SemanticRule):
    """Evaluates whether the value of a property is between a min/max.

    Evaluates whether the value of a property falls within a range specified
    by a min, max, and inclusive parameter. The inclusive parameter is a 
    Boolean and indicates whether the range should be inclusive of the min and
    max parameters.

    Parameters
    ----------
    value : array-like of int or float of length=2. Optional
        Contains min and max values

    instance : ML Studio object
        The instance of a class containing reference attribute

    attribute_name : str
        The name of the attribute containing the min and max values 

    inclusive : bool
        If True, the range is inclusive of min/max values.

    """
    def __init__(self, instance, attribute_name, reference_value,
                 array_ok=False, inclusive=True, **kwargs):
        super(BetweenRule, self).__init__(instance=instance,
                                        attribute_name=attribute_name,
                                        reference_value=reference_value,
                                        array_ok=array_ok,
                                        **kwargs)   
        self._inclusive = inclusive

    def _validate_params(self, value):
        super(BetweenRule, self)._validate_params(value=value)

        # Confirm reference values contains min and max
        if not is_array(self._reference_value):
            raise TypeError("the reference value must be an array-like \
                of length=2, containing two numbers, min and max.")
        elif len(self._reference_value) != 2:
            raise ValueError("the reference value must be an array-like \
                of length=2, containing two numbers, min and max.")
        elif not isinstance(self._reference_value[0], (int, float)) or \
            not isinstance(self._reference_value[1], (int, float)):
            raise ValueError("the reference value must be an array-like \
                of length=2, containing two numbers, min and max.")

    def _get_evaluation_function(self, value):
        """Creates a function that evaluates an attribute and returns a Boolean."""

        def is_invalid(value):
            """Evaluation function for the BetweenRule class."""                
            if self._inclusive and \
                (value < self._reference_value[0] or\
                    value > self._reference_value[1]):
                return True
            elif not self._inclusive and \
                (value <= self._reference_value[0] or\
                    value >= self._reference_value[1]):
                return True
            else:
                return False

        return is_invalid  


    def _error_message(self):
        msg = "The {attribute} property of the {parentname} class is not between \
            [{min_val},{max_val}]. \
            Invalid value(s): '{value}'.".format(
                attribute=self._target_name,
                parentname=self._parent_name,
                min_val = self._reference_value[0],
                max_val = self._reference_value[1],
                value=self._invalid_values.copy())                    
        
        formatted_msg = format_text(msg)
        return formatted_msg                                    



