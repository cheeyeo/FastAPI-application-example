import os
from typing import Any
import pytest
import requests
from fastapi.testclient import TestClient
import boto3
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import delete
from moto import mock_aws
from dotenv import dotenv_values
from app.core.application import create_app
from app.core.aws_cognito import AWSCognito
# import app.dependencies
from app.dependencies import CognitoDep, get_aws_cognito
from app.models import UserBase, User, RandomItemBase, RandomItem, get_session


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
            "scope": "me randoms aws.cognito.signin.user.admin"
        }
    
    return return_token


@pytest.fixture(name="session", scope="session")
def session_fixture():
    config = {
        **os.environ,
        **dotenv_values(".env.test"),
    }

    postgresql_url = f"postgresql://{config.get('RDS_USERNAME')}:{config.get('RDS_PASSWORD')}@{config.get('RDS_HOSTNAME')}:{config.get('RDS_PORT')}/{config.get('RDS_DB_NAME')}"
    
    engine = create_engine(postgresql_url, connect_args={})
    
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="user", scope="session")
def user_fixture(session):
    db_user = User(
        username="test_username",
        email="test_mail@test.com",
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)


@pytest.fixture(name="client", scope="session")
def client_fixture(session, user, mock_cognito_client):
    # Overrides the database dependency to use the test session
    def get_session_override():
        return session
    
    # Overrides the cognito client dependency to use the test client
    def get_aws_cognito_override():
        return mock_cognito_client

    app = create_app()
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_aws_cognito] = get_aws_cognito_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

    # clear data from test database
    for model in [RandomItem, User]:
        stmt = delete(model)
        session.exec(stmt)
        session.commit()


@pytest.fixture()
def token(user, mock_cognito_client, mock_token, client, monkeypatch):
    monkeypatch.setenv("AWS_REGION", mock_cognito_client.region)
    monkeypatch.setenv("AWS_USER_POOL_ID", mock_cognito_client.user_pool_id)
    monkeypatch.setenv("AWS_COGNITO_APP_CLIENT_ID", mock_cognito_client.client_id)
    monkeypatch.setenv("AWS_COGNITO_APP_CLIENT_SECRET", mock_cognito_client.client_secret)

    # Stub the decode_token function to return a mock token with custom user scopes
    monkeypatch.setattr(AWSCognito, "decode_token", mock_token)

    resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})
    assert resp.status_code == 200
    token = resp.json()['access_token']
    assert token is not None

    return token