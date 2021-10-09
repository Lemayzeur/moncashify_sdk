import sys

class Error(Exception):
    """Base class for other exceptions"""
    def __init__(self, key, message="Caught error"):
        self.traceback = sys.exc_info()
        self.key = key
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'<{self.key}> {self.message}'

class AmountError(Error):
    def __init__(self, key, message="Amount should be integer or float"):
        super().__init__(key, message)

class ZeroAmountError(Error):
    def __init__(self, key, message="Amount should be greater than zero(0)"):
        super().__init__(key, message)

class NegativeAmountError(Error):
    def __init__(self, key, message="Amount should be greater than zero(0)"):
        super().__init__(key, message)

class CredentialError(Error):
    def __init__(self, key, message="Invalid type: It should be string"):
        super().__init__(key, message)

class DebugError(Error):
    def __init__(self, key, message="Invalid type: It should be boolean"):
        super().__init__(key, message)

class InvalidPhoneNumberError(Error):
    def __init__(self, key, message="This phone number is not a valid phone number in Haiti"):
        super().__init__(key, message)

class DescriptionError(Error):
    def __init__(self, key, message="Should be a text less than 255 characters"):
        super().__init__(key, message)

class TokenError(Error):
    def __init__(self, status_code, error, message="Error while getting the token"):
        self.status_code = status_code
        self.message = message
        self.error = error
        super().__init__(status_code, message)

    def __str__(self):
        return f'Error {self.status_code} [{self.error}]: {self.message}'

class QueryError(Error):
    def __init__(self, status_code, error, message="Error while fetching data"):
        self.status_code = status_code
        self.message = message
        self.error = error
        super().__init__(status_code, message)

    def __str__(self):
        return f'Error {self.status_code} [{self.error}]: {self.message}'

class OrderNotFoundError(Error):
    def __init__(self, key, message="Order not found"):
        super().__init__(key, message)

class TransactionNotFoundError(Error):
    def __init__(self, key, message="Transaction not found"):
        super().__init__(key, message)