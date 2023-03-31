import string
from enum import Enum

from .utils import Bet

class MessageTypes(str, Enum):
    # Client messages
    SUBMIT = "S" # Payload: [Bet]
    GET_WINNERS = "G" # Payload: None

    # Server messages
    SUBMIT_RESULT = "R" # Payload: str
    WINNERS = "W" # Payload: [str]


SPLIT_CHAR = "\n"

class Message:
    def __init__(self, type: str, payload):
        self.type = type
        self.payload = payload

    def from_string(message_string: str) -> "Message":
        type = MessageTypes(message_string[0])
        rest = message_string[1:]
        if type == MessageTypes.SUBMIT:
            bets = [Bet.from_string(x) for x in rest.split(SPLIT_CHAR)]
            return Message(type, bets)
        elif type == MessageTypes.GET_WINNERS:
            return Message(type, rest)
        raise Exception("Unknown message type")

    def to_string(self) -> string:
        encoded = self.type
        if self.type == MessageTypes.SUBMIT_RESULT:
            encoded += self.payload
        elif self.type == MessageTypes.WINNERS:
            encoded += SPLIT_CHAR.join(self.payload)
        else:
            raise Exception("Not implemented")
        return encoded