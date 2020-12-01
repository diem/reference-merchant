class PaymentServiceException(Exception):
    pass


class WrongReceiverAddressException(PaymentServiceException):
    pass


class PaymentForSubaddrNotFoundException(PaymentServiceException):
    pass


class PaymentStatusException(PaymentServiceException):
    pass


class PaymentExpiredException(PaymentServiceException):
    pass


class PaymentOptionNotFoundException(PaymentServiceException):
    pass
