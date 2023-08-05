from karp5.errors import KarpException

""" Class for exceptions generated by the parser modules
"""


class QueryError(KarpException):
    def __init__(self, message, debug_msg="", status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.debug_msg = debug_msg or message
        if status_code is None:
            self.status_code = 400
        KarpException.__init__(
            self,
            "malformed query: " + message,
            status_code=status_code,
            payload=payload,
            debug_msg=debug_msg,
            user_msg=message,
        )

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


class AuthenticationError(KarpException):
    def __init__(self, message, status_code=None, payload=None):
        if status_code is None:
            status_code = 401
        super().__init__(
            self, "Authentication Exception: " + message, status_code=status_code, payload=payload,
        )

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


class BulkifyError(KarpException):
    def __init__(self, message, bulk_info):
        super().__init__(self, f"Bulkify error: {message}\nbulk_info = {bulk_info}")
