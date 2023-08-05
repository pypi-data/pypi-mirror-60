import json

class BaseObject(object):

    @classmethod
    def decode_json(cls, data):
        if not data:
            return None

        data = data.copy()

        return data
