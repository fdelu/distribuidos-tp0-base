import json
import string

from .utils import Bet

class Message:
    # Client messages
    SUBMIT_TYPE = "submit" # Payload: [Bet]
    GET_WINNERS_TYPE = "get_winners" # Payload: None

    # Server messages
    SUBMIT_RESULT_TYPE = "submit_result" # Payload: str
    WINNERS_TYPE = "winners" # Payload: [str]

    def __init__(self, type: string, payload):
        self.type = type
        self.payload = payload

    def from_json(data) -> "Message":
        parsed = json.loads(data)
        type = parsed["type"]
        payload = parsed["payload"]
        if type == Message.SUBMIT_TYPE:
            bets = [Bet.from_dict(x) for x in payload]
            return Message(type, bets)
        elif type == Message.GET_WINNERS_TYPE:
            return Message(type, payload)
        raise Exception("Unknown message type")

    def to_json(self) -> string:
        if self.type not in (self.SUBMIT_RESULT_TYPE, self.WINNERS_TYPE):
            raise Exception("Not implemented")
        return json.dumps(vars(self))