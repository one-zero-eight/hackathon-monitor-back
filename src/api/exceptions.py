__all__ = [
    "NoCredentialsException",
    "IncorrectCredentialsException",
    "NotEnoughPermissionsException",
    "UserAlreadyExistsException",
    "InvalidRedirectUri",
    "UserNotFound",
    "EmailFlowNotFound",
    "ClientNotFound",
    "ActionNotFoundException",
    "ViewNotFoundException",
    "UserAlreadyHasEmail",
    "ArgumentRequiredException",
    "WrongArgumentTypeException",
    "SQLQueryError",
    "SSHQueryError",
]

from typing import Optional

from fastapi import HTTPException
from starlette import status


class NoCredentialsException(HTTPException):
    """
    HTTP_401_UNAUTHORIZED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.responses[401]["description"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    responses = {
        401: {
            "description": "No credentials provided",
            "headers": {"WWW-Authenticate": {"schema": {"type": "string"}}},
        }
    }


class IncorrectCredentialsException(HTTPException):
    """
    HTTP_401_UNAUTHORIZED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.responses[401]["description"],
        )

    responses = {401: {"description": "Could not validate credentials"}}


class NotEnoughPermissionsException(HTTPException):
    """
    HTTP_403_FORBIDDEN
    """

    def __init__(self, authenticate_header: Optional[str] = None):
        if authenticate_header is None:
            super().__init__(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self.responses[403]["description"],
            )
        else:
            super().__init__(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self.responses[403]["description"],
                headers={"WWW-Authenticate": authenticate_header},
            )

    responses = {403: {"description": "Not enough permissions"}}


class InvalidRedirectUri(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.responses[400]["description"],
        )

    responses = {400: {"description": "Invalid redirect_uri URL"}}


class UserNotFound(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.responses[404]["description"],
        )

    responses = {404: {"description": "User with this id not found"}}


class EmailFlowNotFound(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.responses[404]["description"],
        )

    responses = {404: {"description": "EmailFlow with this pair (user_id, auth_code) not found"}}


class ClientNotFound(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.responses[404]["description"],
        )

    responses = {404: {"description": "Client with this id not found"}}


class UserAlreadyExistsException(HTTPException):
    """
    HTTP_409_CONFLICT
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.responses[409]["description"],
        )

    responses = {409: {"description": "User already exists"}}


class UserAlreadyHasEmail(HTTPException):
    """
    HTTP_409_CONFLICT
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.responses[409]["description"],
        )

    responses = {409: {"description": "User already has this email"}}


class ActionNotFoundException(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self, action_alias: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with alias `{action_alias}` not found",
        )

    responses = {404: {"description": "Action with this alias not found"}}


class ArgumentRequiredException(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self, argument_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Argument `{argument_name}` is required",
        )

    responses = {400: {"description": "Argument is required"}}


class WrongArgumentTypeException(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self, argument_name: str, argument_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Argument `{argument_name}` must be of type `{argument_type}`",
        )

    responses = {400: {"description": "Argument must be of type"}}


class ViewNotFoundException(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self, view_alias: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"View with alias `{view_alias}` not found",
        )

    responses = {404: {"description": "View with this alias not found"}}


class SQLQueryError(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    responses = {400: {"description": "SQL query error"}}


class SSHQueryError(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    responses = {400: {"description": "SSH query error"}}
