"""
DBus
"""

import logging
import os
import socket
import struct
import subprocess
import platform

from .types import FunctionTypes, Status, Variable, VariableTypes, ComponentTypes

TCP_IP = os.getenv("DBUSCOSIM_TCPIP", "127.0.0.1")
TCP_PORT = int(os.getenv("DBUSCOSIM_TCPPORT", "6340"))
BUFFER_SIZE = int(os.getenv("DBUSCOSIM_BUFFERSIZE", "1024")) * 2
CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



_p = None


def start_DBus():
    """
    Start DBus
    """
    global _p
    if platform.system() == "Darwin":
        osname = "OSX32"
    elif platform.system() == "Windows":
        osname = "WIN64"  #TODO: support 32 bit in future
    else:
        #TODO: Add Linux support for ubuntu and redhat
        raise NotImplementedError("Linux is currently not tested. Please contact developer for support.")

    _p = subprocess.Popen("./DBUS_CMD", cwd=os.path.abspath(os.path.join(CURRENT_DIRECTORY, "library/{osname}/".format(osname=osname))))


def stop_DBus():
    """
    stop DBus
    """
    global _p
    if _p is not None:
        _p.kill()
    _p = None


class DBus(object):
    """
    DBus component
    """

    type = None
    variable_struct_mapping = {
        VariableTypes.Integer: "i",
        VariableTypes.Float64: "d",
        VariableTypes.Float32: "f",
        VariableTypes.Boolean: "c",
    }

    def __init__(self, name, variables, type=None):

        self._name = name
        self._variables = []

        self._is_connected = False

        self._variables = [Variable(name, type) for name, type in variables.items()]
        for x in self._variables:
            assert x.type in VariableTypes, "Unknown type received {} for {}".format(x.type, x.name)

        if type is None:
            self._type = self._length_in_bytes(ComponentTypes.SLAVE.value)  # Slave
        else:
            # TODO: Check if self._type is the right type
            self._type = type

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        if self._is_connected:
            self._disconnect()

    def _connect(self):
        ft = FunctionTypes.CONNECTION.value

        self._socket.connect((TCP_IP, TCP_PORT))
        logger.info("Connecting ...")

        data = self._recv(ft, assertion=True)  # connection status

        self._is_connected = True
        logger.info("Successfully connected to DBus")

        return data

    def _register_component(self):
        ft = FunctionTypes.REGISTERCOMPONENT.value
        data = self._type + self._name.encode()
        self._send(ft, data)
        data = self._recv(ft, assertion=True)
        logger.info("Successfully registered to DBus")

        return data

    def _register_component_variables(self):

        ft = FunctionTypes.REGISTERCOMPONENTVARIABLES.value

        # TODO: Add types for variables, currently defaults to 02
        data = ",".join(v.name for v in self._variables) + ","
        l = self._length_in_bytes(len(self._variables), 2)
        data = l + data.encode() + bytes([v.type.value for v in self._variables])
        self._send(ft, data)

        data = self._recv(ft, assertion=True)
        logger.info("Successfully registered component variables to DBus")

        component_information = self._request_component_information()

        component = {"name": "", "variables": {"names": [], "types": []}}
        for c in component_information:
            if c["name"] == self._name:
                component = c

        assert component["name"] == self._name, "Error occurred in retrieving variable names from DBus: {}".format(component)

        ordered_variables_names = component["variables"]["names"]
        ordered_variables_types = component["variables"]["types"]

        self._variables = [Variable(name, type) for name, type in zip(ordered_variables_names, ordered_variables_types)]

        return data

    def _request_component_information(self):

        ft = FunctionTypes.REQUESTCOMPONENTINFORMATION.value

        self._send(ft)
        data = self._recv(ft)

        assert data != Status.ERROR.value, "Received ERROR status from DBus. Please check the error register."

        logger.debug("%s", data)

        number_of_components = data[0]
        data = data[1:]
        data = data.split(b",", number_of_components)
        components = data[:-1]
        data = data[-1]
        component_variables = {}
        for component in components:
            component_variables[component] = {}

        total_size = 0
        for component in components:
            b2, b1 = data[0], data[1]
            size = b2 * 0xff + b1
            component_variables[component]["size"] = b2 * 0xff + b1
            data = data[2:]

            total_size = total_size = size

        variable_names = data.split(b",", total_size)[:-1]

        variable_types = data.split(b",", total_size)[-1]

        for component in components:
            component_variables[component]["variables"] = variable_names[0:component_variables[component]["size"]]
            variable_names = variable_names[component_variables[component]["size"]:]

        for component in components:
            variables = component_variables[component]["variables"]
            component_variables[component]["types"] = []
            for _ in variables:
                component_variables[component]["types"].append(VariableTypes(variable_types[0]))
                variable_types = variable_types[1:]

        result = []

        for component in components:

            component_dict = {}
            component_dict["name"] = component.decode()
            av = component_variables[component]
            av.pop("size")
            av["names"] = [v.decode() for v in av.pop("variables")]
            component_dict["variables"] = av

            result.append(component_dict)

        return result

    def _subscribe_component_variables(self, names, variables):
        ft = FunctionTypes.SUBSCRIBECOMPONENTVARIABLES.value

        if isinstance(names, (str, bytes, bytearray)) or isinstance(variables, (str, bytes, bytearray)):
            raise TypeError("names and variables must be a list or a tuple")

        number_of_components = self._length_in_bytes(len(names))
        name_of_active_components = ",".join(names).encode() + b','
        number_of_variables_per_component = self._length_in_bytes(len(variables), 2)
        name_of_variables_per_components = ",".join(variables).encode() + b','

        data = number_of_components + name_of_active_components + number_of_variables_per_component + name_of_variables_per_components

        self._send(ft, data)

        data = self._recv(ft, assertion=True)
        return data

    def _request_component_variable_content(self, names, variables):

        ft = FunctionTypes.REQUESTCOMPONENTVARIABLECONTENT.value

        if isinstance(names, (str, bytes, bytearray)) or isinstance(variables, (str, bytes, bytearray)):
            raise TypeError("names and variables must be a list or a tuple")

        number_of_components = self._length_in_bytes(len(names))
        name_of_active_components = ",".join(names).encode() + b','
        number_of_variables_per_component = self._length_in_bytes(len(variables), 2)
        name_of_variables_per_components = ",".join(variables).encode() + b','

        data = number_of_components + name_of_active_components + number_of_variables_per_component + name_of_variables_per_components

        self._send(ft, data)

        data = self._recv(ft)
        logger.info("Received data on request for component variable content= %s", data)

        return data

    def _update_component_variables(self, data):

        ft = FunctionTypes.UPDATECOMPONENTVARIABLES.value

        # TODO: Currently this assumes all values are floats. Support int bool doubles and singles.
        b = b''
        for i, datum in enumerate(data):
            b = b + bytearray(struct.pack(self.variable_struct_mapping[self._variables[i].type], datum))[::-1]

        self._send(ft, b)

        data = self._recv(ft, assertion=True)
        return data

    def _get_flags(self):

        ft = FunctionTypes.GETFLAGS.value

        self._send(ft)

        data = self._recv(ft)
        # TODO: parse output of flags
        assert data != Status.ERROR.value, "Received ERROR status from DBus. Please check the error register."

        logger.info("Received data for get flags %s", data)

    def _set_flags(self, flags):

        ft = FunctionTypes.SETFLAGS.value

        data = self._length_in_bytes(*flags)
        self._send(ft, data)
        self._recv(ft, assertion=True)

    def _get_local_flags(self):
        ft = FunctionTypes.GETLOCALFLAG.value

        self._send(ft)

        data = self._recv(ft)
        # TODO: parse output of local flags
        logger.info("Received data for get flags %s", data)
        return data

    def _set_local_flags(self):
        ft = FunctionTypes.SETLOCALFLAG.value

        self._send(ft)

        data = self._recv(ft, assertion=True)
        return data

    def _get_error(self):
        ft = FunctionTypes.GETERROR.value

        self._send(ft)

        data = self._recv(ft)
        # TODO: parse output of error
        logger.info("Received data for error %s", data)
        return data

    def _set_error(self):
        ft = FunctionTypes.SETERROR.value

        self._send(ft)

        data = self._recv(ft, assertion=True)
        return data

    def _clear(self):
        ft = FunctionTypes.CLEAR.value
        self._send(ft)
        self._recv(ft, assertion=True)

    def _get_names(self):
        ft = FunctionTypes.GETNAMES.value
        self._send(ft)
        data = self._recv(ft)
        # TODO: parse output of get names
        logger.info("Received data for get names %s", data)

    def _disconnect(self):
        ft = FunctionTypes.DISCONNECT.value
        self._send(ft)
        logger.info("Disconnecting %s", self._name)
        self._is_connected = False

    def _recv(self, ft, assertion=False):
        data = self._socket.recv(BUFFER_SIZE)
        logger.debug("Received data %s from %s action", data, FunctionTypes(ft).name)
        data = self._decode(data, ft)
        if assertion is True:
            assert data == Status.SUCCESS.value, "Something went wrong with action {rft}".format(rft=FunctionTypes(ft).name)
        logger.debug("Message Content = %s", data)
        return data

    def _send(self, ft, data=b""):
        """
        ft: hex
        data: bytes
        """
        function_type = self._length_in_bytes(ft)
        logger.debug("Function Type = %s", function_type)
        logger.debug("data = %s", data)

        message_content = function_type + data
        header = self._length_in_bytes(len(message_content), 4)

        logger.debug("header = %s", header)
        logger.debug("message_content = %s", message_content)
        message = (header + message_content)

        logger.debug("Sending data %s as %s action", message, FunctionTypes(ft).name)
        self._socket.send(message)

        return data

    @classmethod
    def _decode(cls, data, ft):
        data = [i for i in data]
        size = cls._sizeof(*data[0:4])  # TODO: Fix return size calculation and use for assertion
        logger.debug("Size of data is interpreted as %s", size)

        assert data[4] == ft, "Unrecognized return type for action {rft}, got {ft}".format(rft=FunctionTypes(ft).name, ft=data[4])

        return bytes(data[5:])

    @staticmethod
    def _sizeof(b4, b3, b2, b1):
        return b1 + 0xff * b2 + 0xff * 0xff * b3 + 0xff * 0xff * 0xff * b4

    @staticmethod
    def _length_in_bytes(length, number_of_bytes=1):
        header_size = bytes([length >> i & 0xff for i in (8 * (number_of_bytes - j - 1) for j in range(0, number_of_bytes))])
        return header_size


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    a = DBus(name="DBus1", variables={})

    a._request_component_information()
