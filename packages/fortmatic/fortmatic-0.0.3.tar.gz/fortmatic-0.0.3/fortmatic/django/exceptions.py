class FortmaticDjangoException(Exception):
    pass


class UnsupportedAuthMode(FortmaticDjangoException):
    pass


class PublicAddressDoesNotExist(FortmaticDjangoException):
    pass


class UserEmailMissmatch(FortmaticDjangoException):
    pass


class UnableToLoadUserFromIdentityToken(FortmaticDjangoException):
    pass


class InvalidIdentityToken(FortmaticDjangoException):
    pass


class InvalidSignerAddress(FortmaticDjangoException):
    pass


class InvalidChallengeMessage(FortmaticDjangoException):
    pass
