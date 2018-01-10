"""
Docstring
"""
import time

from pydbus.dbus import *
from pydbus.log import setup_logger

if __name__ == "__main__":

    setup_logger()

    a1 = DBus(
        name="M01",
        variables={"time": VariableTypes.Integer},
    )

    a1._connect()

    a1._register_component()

    a1._register_component_variables()

    a2 = DBus(
        name="SL01",
        variables={
            "voltage": VariableTypes.Float64,
            "current": VariableTypes.Float64,
        },
    )

    a2._connect()

    a2._register_component()

    a2._register_component_variables()

    a2._request_component_information()
