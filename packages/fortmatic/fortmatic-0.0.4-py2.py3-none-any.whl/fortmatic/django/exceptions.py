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
