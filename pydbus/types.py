# -*- coding: utf-8 -*-
"""
Messages codes
"""

from enum import Enum
from collections import namedtuple

Variable = namedtuple("Variable", ["name", "type"])


class Status(Enum):
    """Status Enum"""
    SUCCESS = b"\x01"
    ERROR = b"\x11"


class FunctionTypes(Enum):
    """FunctionTypes Enum"""
    CONNECTION = 0x01
    REGISTERCOMPONENT = 0x0A
    REGISTERCOMPONENTVARIABLES = 0x0B
    REQUESTCOMPONENTINFORMATION = 0x0C
    SUBSCRIBECOMPONENTVARIABLES = 0x0D
    REQUESTCOMPONENTVARIABLECONTENT = 0x0E
    UPDATECOMPONENTVARIABLES = 0x0F
    GETFLAGS = 0x10
    SETFLAGS = 0x11
    SETLOCALFLAG = 0x12
    GETLOCALFLAG = 0x13
    GETERROR = 0x14
    SETERROR = 0x15
    CLEAR = 0x16
    GETNAMES = 0x17
    DISCONNECT = 0x18


class ComponentTypes(Enum):
    """VariableTypes Enum"""
    SLAVE = 0x01
    MASTER = 0x0F
    SUPERVISOR = 0xAF


class VariableTypes(Enum):
    """VariableTypes Enum"""
    Integer = 1
    Float64 = 2
    Float32 = 3
    Boolean = 4
