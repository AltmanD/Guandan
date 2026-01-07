import numpy as np
import json


class RandomAgent():
    def __init__(self, id=0):
        self.id = id

    def received_message(self, message):
        message = json.loads(str(message))
        # print(self.id, message)
        if "actionList" in message:
            upper = message['indexRange'] + 1
            return np.random.randint(0, upper)