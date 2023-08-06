class ClientError(Exception):
    pass


class TerraAPIError(Exception):
    pass


class ValidationError(Exception):
    pass


class DenomNotFoundError(Exception):
    pass


class DenomIncompatibleError(Exception):
    pass


class AccountNotFoundWarning(Warning):
    pass
