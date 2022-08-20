"""MySQLdb wrapper for easy usage and encryption"""

from asyncio.base_subprocess import BaseSubprocessTransport
import copy
import datetime
from subprocess import call
import warnings

import MySQLdb
from MySQLdb.cursors import Cursor

import encryption
from .encryption import Id

from .logs import logger

warnings.filterwarnings("ignore", category=MySQLdb.Warning)

MYSQL_SERVER_IS_GONE = 2006
MYSQL_TABLE_ALREADY_EXISTS = 1050


class Empty:
    pass


def diff(other):
    return {k: v for k, v in vars(other).items() if k not in vars(Empty).keys() and not callable(other.__dict__[k])}


def getattribute(cls, name):
    if name.startswith("_") or callable(type.__getattribute__(cls, name)) or isinstance(type.__getattribute__(cls, name), property):
        return type.__getattribute__(cls, name)
    return BaseOperator(name)

class ClassOrInstanceMethod(object):
    def __init__(self, f):
        self.f = f
    
    def __get__(self, instance, owner):
        if instance is None:
            instance = owner
        return self.f.__get__(instance, owner)
    
class BaseMetaClass(object):
    def __new__(cls, clsname, superclasses, attributedict):
        cls.__getattribute__ = lambda a, b: getattribute(a, b)
        return type.__new__(cls, clsname, superclasses, attributedict)
    
class Base(metaclass=BaseMetaClass):
    '''Base classs for all databases'''
    
    def __init__(self, session=None, *args, **kwargs):
        dic = diff(type(self))
        for key, value in dic.items():
            if isinstance(getattr(type(self), key, None), property):
                continue
            setattr(self, key, value)
        for arg in args:
            for key, value in arg.items():
                if key in dic:
                    setattr(self, key, value)
        for key, value in kwargs.items():
            if key in dic:
                setattr(self, key, value)
        self._session = session
    
    def __deepcopy__(self, memo):
        new_obj = self.__class__(self._session)
        for key, value in self.get_table_dict().items():
            setattr(new_obj, key, copy.deepcopy(value, memo))
        return new_obj
    
    @classmethod
    def get_from_id(cls, session, obj_id):
        return session.query(cls).where(cls.id == obj_id).first()
    
    @ClassOrInstanceMethod
    def get_table_dict(self):
        '''Gets al fields of the table.'''
        table_dict = {}
        for key, value in vars(self).items():
            if key.startswith("_") or isinstance(value, (property, classmethod, staticmethod)) or callable(value):
                continue
            table_dict[key] = value
        return table_dict
    
    def get_api_dict(self):
        '''Gets all fields of the table, expect bytes field.'''
        table_dict = self.get_table_dict()
        api_dict = {}
        for key, value in table_dict.items():
            if not isinstance(object.__getattribute__(type(self), key), bytes):
                api_dict[key] = value
        return api_dict