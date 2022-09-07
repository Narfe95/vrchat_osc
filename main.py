"""
Requires two parameters on the avatar on which it will be used.

CreateParty: bool
NewWorld: bool

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
        dispatcher.map(f"{self.__osc_params.base_osc_address}/CreateParty", self.__create_party)
        dispatcher.map(f"{self.__osc_params.base_osc_address}/NewWorld", self.__new_world)
        self.server = ThreadingOSCUDPServer((self.__osc_params.ip, self.__osc_params.receiver_port), dispatcher)

    def __create_party(self, _, *args):
        # Fetch players in instance and create "party"
        if args[0]:  # Only run if the parameter is set to true
            print("New party requested.")
            self.__party_created = True
            self.__send_message("CreateParty", False)
            # Create party code here

    def __new_world(self, _, *args):
        # Find new world to create instance for and invite players in party
        if args[0] and self.__party_members:  # Only run if the parameter is set to true and a party has been formed
            print("New world requested...")
            # New world code here and invite party
            # Return the players in party to parameter in-game
        if args[0]:
            self.__send_message("NewWorld", False)

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
