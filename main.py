"""
Requires two parameters on the avatar on which it will be used.

Suggested is to set these parameters using a toggle to let this script set it back to False.

"""
from dataclasses import dataclass
from typing import Union

from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import ThreadingOSCUDPServer

IP = "127.0.0.1"
RECEIVER_PORT = 9001
SENDER_PORT = 9000
BASE_ADDRESS = "/avatar/parameters"


@dataclass
class OSCParams:
    ip: str
    receiver_port: int
    sender_port: int
    base_osc_address: str


class OSC:

    def __init__(self, osc_params: OSCParams):
        self.__osc_params = osc_params
        self.__party_members = list()
        dispatcher = Dispatcher()
        dispatcher.map(f"{self.__osc_params.base_osc_address}/ExampleAction", self.__example_action)
        self.server = ThreadingOSCUDPServer((self.__osc_params.ip, self.__osc_params.receiver_port), dispatcher)

    def __example_action(self, _, *args):
        pass

    def __send_message(self, parameter: str, value: Union[int, float, bytes, str, bool, tuple, list]) -> None:
        __client = SimpleUDPClient(self.__osc_params.ip, self.__osc_params.sender_port)
        __client.send_message(f"{self.__osc_params.base_osc_address}/{parameter}", value)
        print(f"Sent message to '{self.__osc_params.base_osc_address}/{parameter}' with a value of '{value}'")


if __name__ == "__main__":
    osc = OSC(OSCParams(IP, RECEIVER_PORT, SENDER_PORT, BASE_ADDRESS))
    print(f"Starting server")
    try:
        osc.server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting...")
