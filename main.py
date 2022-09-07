"""
Requires two parameters on the avatar on which it will be used.

Suggested is to set these parameters using a toggle to let this script set it back to False.

"""
from asyncio import get_running_loop, new_event_loop, set_event_loop, AbstractEventLoop
from dataclasses import dataclass
from time import sleep
from typing import Union

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer


@dataclass
class OSCParams:
    ip: str = "127.0.0.1"
    receiver_port: int = 9001
    sender_port: int = 9000
    base_address: str = "/avatar/parameters"
    chatbox_input: str = "/chatbox/input"
    sleep_time: int = 1


class OSC:

    def __init__(self, osc_params: OSCParams, text: str):
        self.osc_params = osc_params
        self.party_members = list()
        self.__text = text
        self.__task = None
        self.__task_running = False
        dispatcher = Dispatcher()
        dispatcher.map(f"{self.__osc_params.base_address}/toggle_text", self.__toggle_text)
        self.server = ThreadingOSCUDPServer((self.__osc_params.ip, self.__osc_params.receiver_port), dispatcher)

    def __get_loop(self) -> AbstractEventLoop:
        try:
            return get_running_loop()
        except RuntimeError:
            loop = new_event_loop()
            set_event_loop(loop)
            return loop

    def __toggle_text(self, _, *args):
        self.__task_running = args[0]
        if self.__task_running:
            self.__get_loop().run_until_complete(self.__message_dispatcher())

    async def __message_dispatcher(self):
        self.__task = self.__get_loop().create_task(self.__send_messages())

    async def __send_messages(self):
        while self.__task_running:
            self.__send_chat_message(self.__text)
            sleep(self.__osc_params.sleep_time)

    def __send_param(self, parameter: str, value: Union[int, float, bytes, str, bool, tuple, list]) -> None:
        __client = SimpleUDPClient(self.__osc_params.ip, self.__osc_params.sender_port)
        __client.send_message(f"{self.__osc_params.base_address}/{parameter}", value)
        print(f"Sent message to '{self.__osc_params.base_address}/{parameter}' with a value of '{value}'")

    def __send_chat_message(self, message: str):
        __client = SimpleUDPClient(self.__osc_params.ip, self.__osc_params.sender_port)
        __client.send_message(f"{self.__osc_params.base_address}", message)
        print(f"Sent message to '{self.__osc_params.base_address}' with a value of '{message}'")


if __name__ == "__main__":
    osc = OSC(OSCParams(), "Hello")
    print(f"Starting server")
    try:
        osc.server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting...")
