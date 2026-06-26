class INEIError(Exception):
    pass


class INEIAPIError(INEIError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class INEINotFoundError(INEIAPIError):
    pass


class INEITimeoutError(INEIAPIError):
    pass
