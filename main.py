"""
Requires two parameters on the avatar on which it will be used.

Suggested is to set these parameters using a toggle to let this script set it back to False.

"""
from dataclasses import dataclass
from typing import Union

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


@dataclass
class OSCParams:
    ip: str = "127.0.0.1"
    receiver_port: int = 9001
    sender_port: int = 9000
    base_osc_address: str = "/avatar/parameters"


class OSC:

    def __init__(self, osc_params: OSCParams):
        self.osc_params = osc_params
        self.party_members = list()
        dispatcher = Dispatcher()
        dispatcher.map(f"{self.osc_params.base_osc_address}/ExampleAction", self.example_action)
        self.server = ThreadingOSCUDPServer((self.osc_params.ip, self.osc_params.receiver_port), dispatcher)

    def example_action(self, _, *args):
        pass

    def send_message(self, parameter: str, value: Union[int, float, bytes, str, bool, tuple, list]) -> None:
        client = SimpleUDPClient(self.osc_params.ip, self.osc_params.sender_port)
        client.send_message(f"{self.osc_params.base_osc_address}/{parameter}", value)
        print(f"Sent message to '{self.osc_params.base_osc_address}/{parameter}' with a value of '{value}'")


if __name__ == "__main__":
    osc = OSC(OSCParams())
    print(f"Starting server")
    try:
        osc.server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting...")
