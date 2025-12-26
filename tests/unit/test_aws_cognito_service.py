from botocore.exceptions import ClientError
import pytest
from fastapi import HTTPException
from app.services.cognito import AuthService
import json


def test_resend_confirmation(mocker, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "resend_confirmation_code", return_value=True)

    resp = AuthService.resend_confirmation("test_user", mock_cognito_client)
    
    assert json.loads(resp.body.decode('utf-8')) == {"message": "Confirmation code sent successfully"}


def test_resend_confirmation_no_user(mocker, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "resend_confirmation_code", side_effect=ClientError(error_response={"Error": {"Code": "UserNotFoundException"}}, operation_name="resend_confirmation_code"))

    with pytest.raises(HTTPException) as err:
        AuthService.resend_confirmation("test_user", mock_cognito_client)
    
    assert err.value.status_code == 404
    assert err.value.detail == "User not found"


def test_resend_confirmation_limit_exceeded(mocker, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "resend_confirmation_code", side_effect=ClientError(error_response={"Error": {"Code": "LimitExceededException"}}, operation_name="resend_confirmation_code"))

    with pytest.raises(HTTPException) as err:
        AuthService.resend_confirmation("test_user", mock_cognito_client)
    
    assert err.value.status_code == 429
    assert err.value.detail == "Limit exceeded"


def test_resend_confirmation_internal_error(mocker, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "resend_confirmation_code", side_effect=ClientError(error_response={"Error": {"Code": "InternalErrorException"}}, operation_name="resend_confirmation_code"))

    with pytest.raises(HTTPException) as err:
        AuthService.resend_confirmation("test_user", mock_cognito_client)
    
    assert err.value.status_code == 500
    assert err.value.detail == "Internal server error"
