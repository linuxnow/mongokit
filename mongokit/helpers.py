#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010, Nicolas Clairon
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime

def totimestamp(dt):
    """
    convert a datetime into a float since epoch
    """
    import time
    return time.mktime(dt.timetuple()) + dt.microsecond/1e6

def fromtimestamp(epoch_date):
    """
    convert a float since epoch to a datetime object
    """
    return datetime.datetime.fromtimestamp(epoch_date)

from copy import deepcopy

class i18nDotedDict(dict):
    """
    Dot notation dictionnary access with i18n support
    """
    def __init__(self, dic, doc):
        super(i18nDotedDict, self).__init__(dic)
        self._doc = doc

    def __setattr__(self, key, value):
        from mongokit.schema_document import i18n
        if key in self:
            if isinstance(self[key], i18n):
                self[key][self._doc._current_lang] = value
            else:
                self[key] = value
        else:
           dict.__setattr__(self, key, value) 

    def __getattr__(self, key):
        from mongokit.schema_document import i18n
        if key in self:
            if isinstance(self[key], i18n):
                if self._doc._current_lang not in self[key]:
                    return self[key].get(self._doc._fallback_lang)
                return self[key][self._doc._current_lang]
            return self[key]

    def __deepcopy__(self, memo={}):
        obj = dict(self)
        return deepcopy(obj, memo)

class DotedDict(dict):
    """
    Dot notation dictionnary access
    """
    def __setattr__(self, key, value):
        if key in self:
            self[key] = value
        else:
           dict.__setattr__(self, key, value) 
    def __getattr__(self, key):
        if key in self:
            return self[key]
    def __deepcopy__(self, memo={}):
        obj = dict(self)
        return deepcopy(obj, memo)

class DotExpandedDict(dict): 
    """ 
    A special dictionary constructor that takes a dictionary in which the keys 
    may contain dots to specify inner dictionaries. It's confusing, but this 
    example should make sense. 

    >>> d = DotExpandedDict({'person.1.firstname': ['Simon'], \ 
          'person.1.lastname': ['Willison'], \ 
          'person.2.firstname': ['Adrian'], \ 
          'person.2.lastname': ['Holovaty']}) 
    >>> d 
    {'person': {'1': {'lastname': ['Willison'], 'firstname': ['Simon']}, '2': {'lastname': ['Holovaty'], 'firstname': ['Adrian']}}} 
    >>> d['person'] 
    {'1': {'lastname': ['Willison'], 'firstname': ['Simon']}, '2': {'lastname': ['Holovaty'], 'firstname': ['Adrian']}} 
    >>> d['person']['1'] 
    {'lastname': ['Willison'], 'firstname': ['Simon']} 

    # Gotcha: Results are unpredictable if the dots are "uneven": 
    >>> DotExpandedDict({'c.1': 2, 'c.2': 3, 'c': 1}) 
    {'c': 1} 
    """ 
    # code taken from Django source code http://code.djangoproject.com/
    def __init__(self, key_to_list_mapping): 
        for k, v in key_to_list_mapping.items(): 
            current = self 
            bits = k.split('.') 
            for bit in bits[:-1]: 
               current = current.setdefault(bit, {}) 
            # Now assign value to current position 
            try: 
                current[bits[-1]] = v 
            except TypeError: # Special-case if current isn't a dict. 
                current = {bits[-1]: v} 

class DotCollapsedDict(dict):
    """
    A special dictionary constructor that take a dict and which provides
    a DotExpandedDict.

    >>> DotExpandedDict({'a':{'b':{'c':{'d':3}, 'e':5}, "g":2}, 'f':6})
    {'a.b.c.d': 3, 'a.b.e': 5, 'a.g': 2, 'f': 6}
    """
    def __init__(self, passed_dict):
        assert isinstance(passed_dict, dict), "you must pass a dict instance"
        final_dict = {}
        self._make_dotation(passed_dict, final_dict)
        self.update(final_dict)

    def _make_dotation(self, d, final_dict, key=""):
        for k,v in d.iteritems():
            if isinstance(k, type):
                k = "$%s" % k.__name__
            if isinstance(v, dict) and v != {}:
                if key:
                    _key = "%s.%s" % (key, k)
                else:
                    _key = k
                self._make_dotation(v, final_dict, _key)
            else:
                if not key:
                    final_dict[k] = v
                else:
                    final_dict["%s.%s" % (key, k)] = v