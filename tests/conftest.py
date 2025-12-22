import os
from typing import Any
import pytest
from fastapi.testclient import TestClient
import boto3
import requests
from moto import mock_aws
from app.core.application import create_app
from app.core.aws_cognito import AWSCognito, UserSignup
from app.dependencies import CognitoDep


@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-west-1"
    os.environ["AWS_REGION"] = "us-west-1"


@pytest.fixture(scope="session")
def mock_cognito_client(aws_credentials):
    with mock_aws():
        cognito_client = boto3.client("cognito-idp", region_name="us-west-1")
        user_pool_id = cognito_client.create_user_pool(PoolName="TestUserPool")["UserPool"]["Id"]
        app_client = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName="TestAppClient"
        )

        username = "test_username"
        password = "SecurePassword1234#$%"  # Password must meet security policies.
        email = "test_mail@test.com"

        cognito_client.sign_up(
            ClientId=app_client["UserPoolClient"]["ClientId"],
            Username=username,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
            ],
        )
        
        cognito_client.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=username)

        # access_token = cognito_client.initiate_auth(
        #     ClientId=app_client["UserPoolClient"]["ClientId"],
        #     AuthFlow="USER_PASSWORD_AUTH",
        #     AuthParameters={"USERNAME": username, "PASSWORD": password},
        # )["AuthenticationResult"]["AccessToken"]

        # print(f"CONFTEST ACCESS TOKEN: {access_token}")

        yield AWSCognito(client=cognito_client, region="us-west-1", client_id=app_client["UserPoolClient"]["ClientId"], client_secret="SECRET", user_pool_id=user_pool_id)


@pytest.fixture(scope="session")
def mock_token():
    def return_token(self, token):
        return {
            "sub": "9cc71104-d2b8-4a84-8269-a55b95f5bd23",
            "iss": "https://cognito-idp.us-west-1.amazonaws.com/us-west-1_4ujjMwsfK",
            "client_id": "4pon8gi9t6f6dllka6ap2ihcad",
            "origin_jti": "65e3bb61-b3ba-4156-8ebd-ae6db607310f",
            "event_id": "2e63932a-3583-4265-949c-05f52bb56467",
            "token_use": "access",
            "auth_time": 1662022792,
            "exp": 1662026392,
            "iat": 1662022792,
            "jti": "d5d3f3d9-c02d-41e7-a9da-4443278d61cf",
            "username": "test_username",
        }
    
    return return_token


@pytest.fixture(scope="session")
def app():
    app = create_app()
    yield app


@pytest.fixture(scope="session")
def client(app):
    client = TestClient(app)
    return client
