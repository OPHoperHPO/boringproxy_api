"""Boring Proxy all possible API exceptions"""
import requests


def get_exception(response: requests.Response):
    """
    Initializes the desired error
    :param response: requests response
    :return: Exception
    """
    return {
        401: TokenError(response.text),
        403: AuthError(response.text),
        405: MethodNotAllowed(response.text),
        406: MethodNotAllowed(response.text),  # TODO Remove it when issue #54 will be fixed
        400: BadRequest(response.text),
        500: ServerError(response.text)
    }[response.status_code]


class TokenError(Exception):
    """Token Error Exception"""
    def __init__(self, *args):
        super().__init__(*args)


class AuthError(Exception):
    """Auth Error Exception"""
    def __init__(self, *args):
        super().__init__(*args)


class MethodNotAllowed(Exception):
    """Method Not Allowed Exception"""
    def __init__(self, *args):
        super().__init__(*args)


class BadRequest(Exception):
    """Bad Request Exception"""
    def __init__(self, *args):
        super().__init__(*args)


class ServerError(Exception):
    """Server Error Exception"""
    def __init__(self, *args):
        super().__init__(*args)
