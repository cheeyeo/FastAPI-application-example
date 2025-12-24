import os
import pytest
from fastapi import Depends
import app.dependencies
from app.core.aws_cognito import AWSCognito


def test_get_randoms_not_authenticated(client):
    response = client.get("/randoms")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_randoms_authenticated(client, mock_cognito_client, mock_token, monkeypatch):
    # Stub out the environment variables
    monkeypatch.setenv("AWS_REGION", mock_cognito_client.region)
    monkeypatch.setenv("AWS_USER_POOL_ID", mock_cognito_client.user_pool_id)
    monkeypatch.setenv("AWS_COGNITO_APP_CLIENT_ID", mock_cognito_client.client_id)
    monkeypatch.setenv("AWS_COGNITO_APP_CLIENT_SECRET", mock_cognito_client.client_secret)

    # Stub the cognito function to return the mock client
    monkeypatch.setattr(app.dependencies, "get_aws_cognito", mock_cognito_client)
    monkeypatch.setattr(AWSCognito, "decode_token", mock_token)

    resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})
    assert resp.status_code == 200
    token = resp.json()['access_token']
    assert token is not None

    response = client.get("/randoms", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []


def test_get_randoms_list_authenticated(client, mock_cognito_client, mock_token, monkeypatch):
    # Stub out the environment variables
    monkeypatch.setenv("AWS_REGION", mock_cognito_client.region)
    monkeypatch.setenv("AWS_USER_POOL_ID", mock_cognito_client.user_pool_id)
    monkeypatch.setenv("AWS_COGNITO_APP_CLIENT_ID", mock_cognito_client.client_id)
    monkeypatch.setenv("AWS_COGNITO_APP_CLIENT_SECRET", mock_cognito_client.client_secret)

    # Stub the cognito function to return the mock client
    monkeypatch.setattr(app.dependencies, "get_aws_cognito", mock_cognito_client)
    monkeypatch.setattr(AWSCognito, "decode_token", mock_token)

    resp = client.post("/users/login", data={"username": "test_username", "password": "SecurePassword1234#$%"})
    assert resp.status_code == 200
    token = resp.json()['access_token']
    assert token is not None

    # create a random item
    resp = client.post("/randoms", json={"min_value": 10, "max_value": 20}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["min_value"] == 10
    assert resp.json()["max_value"] == 20

    response = client.get("/randoms", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
