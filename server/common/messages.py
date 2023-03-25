import json
import string

from .utils import Bet

class Message:
    # Client messages
    SUBMIT_TYPE = "submit" # Payload: [Bet]

    # Server messages
    SUBMIT_RESULT_TYPE = "submit_result" # Payload: str

    def __init__(self, type: string, payload):
        self.type = type
        self.payload = payload

    def from_json(data):
        parsed = json.loads(data)
        type = parsed["type"]
        if type == Message.SUBMIT_TYPE:
            bets = [Bet.from_dict(x) for x in parsed["payload"]]
            return Message(type, bets)
        raise Exception("Unknown message type")

    def to_json(self):
        if self.type != self.SUBMIT_RESULT_TYPE:
            raise Exception("Not implemented")
        return json.dumps(vars(self))