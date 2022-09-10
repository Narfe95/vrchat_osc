"""
Requires two parameters on the avatar on which it will be used.

Suggested is to set these parameters using a toggle to let this script set it back to False.

"""
from asyncio import get_running_loop, new_event_loop, set_event_loop, AbstractEventLoop
from dataclasses import dataclass
from time import sleep
from typing import List

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


@dataclass
class OSCParams:
    ip: str = "127.0.0.1"
    receiver_port: int = 9001
    sender_port: int = 9000
    base_address: str = "/avatar/parameters"
    chatbox_osc: str = "/chatbox/input"
    sleep_time: int = 10


class OSC:

    def __init__(self, osc_params: OSCParams, text: List[str]):
        self.osc_params = osc_params
        self.text = text
        self.task = None
        self.task_running = False
        dispatcher = Dispatcher()
        dispatcher.map(f"{self.osc_params.base_address}/toggle_text", self.toggle_text)
        self.server = ThreadingOSCUDPServer((self.osc_params.ip, self.osc_params.receiver_port), dispatcher)

    def kill_send_messages(self):
        if self.get_loop():
            self.task_running = False
            self.get_loop().close()

    def next_string(self):
        while True:  # To avoid running out of strings to generate.
            for string in self.text:
                yield string

    def get_loop(self) -> AbstractEventLoop:
        try:
            return get_running_loop()
        except RuntimeError:
            loop = new_event_loop()
            set_event_loop(loop)
            return loop

    def toggle_text(self, _, *args):
        self.task_running = args[0]
        if self.task_running:
            gen = self.next_string()
            self.get_loop().run_until_complete(self.message_dispatcher(gen))

    async def message_dispatcher(self, gen):
        self.task = self.get_loop().create_task(self.send_messages(gen))

    async def send_messages(self, gen):
        while self.task_running:
            self.send_chat_message(next(gen))
            sleep(self.osc_params.sleep_time)

    def send_chat_message(self, message: str):
        client = SimpleUDPClient(self.osc_params.ip, self.osc_params.sender_port)
        client.send_message(f"{self.osc_params.chatbox_osc}", [message, True])
        print(f"Sent message to '{self.osc_params.chatbox_osc}' with a value of '{message}'")


if __name__ == "__main__":
    lyrics_file = open(file="bee.txt", mode="r")
    lyrics = lyrics_file.read().splitlines()
    lyrics_file.close()
    osc = OSC(OSCParams(sleep_time=3), lyrics)
    print(f"Starting server")
    try:
        osc.server.serve_forever()
    except KeyboardInterrupt:
        osc.kill_send_messages()
        print("Exiting...")
