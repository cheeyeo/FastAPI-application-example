from botocore.exceptions import ClientError
from app.core.aws_cognito import AWSCognito


def test_users_signup(client):
    resp = client.post("/users/signup", json={"username": "test", "email": "test@example.com", "password": "SecurePassword1234#$%"})
    assert resp.status_code == 201
    assert resp.json()["message"] == "User created successfully"
    assert "sub" in resp.json().keys()
    sub = resp.json()["sub"]

    resp = client.get(f"/users/{sub}")
    assert resp.status_code == 200
    user = resp.json()
    assert user["sub"] == sub
    assert user["username"] == "test"
    assert user["email"] == "test@example.com"


def test_users_signup_user_exists(mocker, client, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "user_signup", side_effect=ClientError(error_response={"Error": {"Code": "UsernameExistsException"}}, operation_name="user signup"))
    
    resp = client.post("/users/signup", json={"username": "test", "email": "test@example.com", "password": "SecurePassword1234#$%"})
    
    assert resp.status_code == 409
    assert resp.json() == {"detail": "Account with email exists"}


def test_users_signup_internal_error(mocker, client, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "user_signup", side_effect=ClientError(error_response={"Error": {"Code": "InternalErrorException"}}, operation_name="user signup"))

    resp = client.post("/users/signup", json={"username": "test", "email": "test@example.com", "password": "SecurePassword1234#$%"})

    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error"}


def test_users_login(client, mock_cognito_client):
    resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})
    assert resp.status_code == 200
    assert resp.json()["access_token"] is not None
    assert resp.json()["token_type"] == "bearer"


def test_users_login_not_found(mocker, client, mock_cognito_client):
     mocker.patch.object(mock_cognito_client, "user_signin", side_effect=ClientError(error_response={"Error": {"Code": "UserNotFoundException"}}, operation_name="user signin"))

     resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})

     assert resp.status_code == 404
     assert resp.json() == {"detail": "User does not exist"}


def test_users_login_not_confirmed(mocker, client, mock_cognito_client):
     mocker.patch.object(mock_cognito_client, "user_signin", side_effect=ClientError(error_response={"Error": {"Code": "UserNotConfirmedException"}}, operation_name="user signin"))

     resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})

     assert resp.status_code == 403
     assert resp.json() == {"detail": "Verify your account"}


def test_users_login_unauthorized(mocker, client, mock_cognito_client):
     mocker.patch.object(mock_cognito_client, "user_signin", side_effect=ClientError(error_response={"Error": {"Code": "NotAuthorizedException"}}, operation_name="user signin"))

     resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})

     assert resp.status_code == 401
     assert resp.json() == {"detail": "Incorrect username or password"}


def test_users_login_internal_error(mocker, client, mock_cognito_client):
     mocker.patch.object(mock_cognito_client, "user_signin", side_effect=ClientError(error_response={"Error": {"Code": "InternalErrorException"}}, operation_name="user signin"))

     resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})

     assert resp.status_code == 500
     assert resp.json() == {"detail": "Internal server error"}


def test_users_verify(client, mock_cognito_client):
     resp = client.post("/users/verify", json={"username": "test", "confirmation_code": "12345"})
     assert resp.status_code == 200
     assert resp.json() == {"message": "Account verification successful"}


def test_users_verify_code_mismatch(mocker, client, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "verify_account", side_effect=ClientError(error_response={"Error": {"Code": "CodeMismatchException"}}, operation_name="confirm_signup"))
    
    resp = client.post("/users/verify", json={"username": "test", "confirmation_code": "12345"})
    assert resp.status_code == 400
    assert resp.json() == {"detail": "The provided code does not match the expected value."}


def test_users_verify_code_expired(mocker, client, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "verify_account", side_effect=ClientError(error_response={"Error": {"Code": "ExpiredCodeException"}}, operation_name="confirm_signup"))
    
    resp = client.post("/users/verify", json={"username": "test", "confirmation_code": "12345"})
    assert resp.status_code == 400
    assert resp.json() == {"detail": "The provided code has expired."}


def test_users_verify_code_not_found(mocker, client, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "verify_account", side_effect=ClientError(error_response={"Error": {"Code": "UserNotFoundException"}}, operation_name="confirm_signup"))
    
    resp = client.post("/users/verify", json={"username": "test", "confirmation_code": "12345"})
    assert resp.status_code == 404
    assert resp.json() == {"detail": "User not found"}


def test_users_verify_code_already_verified(mocker, client, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "verify_account", side_effect=ClientError(error_response={"Error": {"Code": "NotAuthorizedException"}}, operation_name="confirm_signup"))
    
    resp = client.post("/users/verify", json={"username": "test", "confirmation_code": "12345"})
    assert resp.status_code == 200
    assert resp.json() == {"detail": "User already verified."}


def test_users_verify_code_internal_error(mocker, client, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "verify_account", side_effect=ClientError(error_response={"Error": {"Code": "InternalErrorException"}}, operation_name="confirm_signup"))
    
    resp = client.post("/users/verify", json={"username": "test", "confirmation_code": "12345"})
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error"}


def test_users_logout_no_token(client):
    resp = client.post("/users/logout")
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


def test_users_logout(client, token):
    resp = client.post("/users/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "Logged out successfully"}


def test_users_logout_wrong_token_format(mocker, client, token, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "logout", side_effect=ClientError(error_response={"Error": {"Code": "InvalidParameterException"}}, operation_name="global_sign_out"))

    resp = client.post("/users/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Access token provided has wrong format"}


def test_users_logout_unauthorized(mocker, client, token, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "logout", side_effect=ClientError(error_response={"Error": {"Code": "NotAuthorizedException"}}, operation_name="global_sign_out"))

    resp = client.post("/users/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid access token provided"}


def test_users_logout_rate_limit(mocker, client, token, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "logout", side_effect=ClientError(error_response={"Error": {"Code": "TooManyRequestsException"}}, operation_name="global_sign_out"))

    resp = client.post("/users/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 429
    assert resp.json() == {"detail": "Too many requests"}

def test_users_logout_internal_error(mocker, client, token, mock_cognito_client):
    mocker.patch.object(mock_cognito_client, "logout", side_effect=ClientError(error_response={"Error": {"Code": "InternalErrorException"}}, operation_name="global_sign_out"))

    resp = client.post("/users/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error"}
