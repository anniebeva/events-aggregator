class ProviderError(Exception):
    """Represent an Events Provider error"""


class ProviderNotFoundError(ProviderError):
    """Represent a not found error from the Events Provider"""