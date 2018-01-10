import time
from pydbus.dbus import DBus
from pydbus.log import setup_logger
from pydbus.status import VariableTypes

import logging

if __name__ == "__main__":

    setup_logger()

    a = DBus(
        name="DBus2",
        variables={},
    )

    a._connect()

    a._register_component()

    a._request_component_information()

    while True:
        a._request_component_information()
        print("Sleeping for 10 second")
        time.sleep(10)
