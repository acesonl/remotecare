class MollieException(Exception):
    resultcode = -1


class NoUsernameException(MollieException):
    resultcode = 20


class NoPasswordException(MollieException):
    resultcode = 21


class InvalidOriginatorException(MollieException):
    resultcode = 22


class RecipientMissingException(MollieException):
    resultcode = 23


class MessageMissingException(MollieException):
    resultcode = 24


class InvalidRecipientException(MollieException):
    resultcode = 25


class InvalidOriginatorException(MollieException):
    resultcode = 26


class InvalidMessageException(MollieException):
    resultcode = 27


class ParameterException(MollieException):
    resultcode = 29


class AuthenticationException(MollieException):
    resultcode = 30


class InsufficientCreditsException(MollieException):
    resultcode = 31


class GatewayUnreachableException(MollieException):
    resultcode = 98


class UnknownException(MollieException):
    resultcode = 99

by_code = dict(
    [(i.resultcode, i) for i in [
        NoUsernameException,
        NoPasswordException, InvalidOriginatorException,
        RecipientMissingException,
        MessageMissingException, InvalidRecipientException,
        InvalidOriginatorException, InvalidMessageException,
        ParameterException, AuthenticationException,
        InsufficientCreditsException, GatewayUnreachableException,
        UnknownException]])
