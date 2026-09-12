"""Erreurs metier exposees par les outils MCP."""


class DataFootError(Exception):
    """Erreur de base du serveur DataFoot."""

    code = "DATAFOOT_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def as_dict(self) -> dict:
        return {"success": False, "error": {"code": self.code, "message": self.message}}


class PlayerNotFoundError(DataFootError):
    code = "PLAYER_NOT_FOUND"


class MultiplePlayersFoundError(DataFootError):
    code = "MULTIPLE_PLAYERS_FOUND"


class DatasetNotFoundError(DataFootError):
    code = "DATASET_NOT_FOUND"


class UnsupportedStatisticError(DataFootError):
    code = "UNSUPPORTED_STATISTIC"


class InvalidFilterError(DataFootError):
    code = "INVALID_FILTER"
