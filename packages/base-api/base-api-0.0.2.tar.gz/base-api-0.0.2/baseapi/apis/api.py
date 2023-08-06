class Api:
    SUCCESS_RESPONSE_CODES = (200, 201)

    @classmethod
    def expose_method(cls, method):
        method.expose = True
        return method

    def __init__(self, client):
        self.client = client
