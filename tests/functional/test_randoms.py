import os
import pytest
from fastapi import Depends
import app.dependencies
from app.core.aws_cognito import AWSCognito


def test_get_randoms_not_authenticated(client):
    response = client.get("/randoms")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_randoms(client, token):
    response = client.get("/randoms", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []


def test_get_randoms_list(client, token):
    # create a random item
    resp = client.post("/randoms", json={"min_value": 10, "max_value": 20}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["min_value"] == 10
    assert resp.json()["max_value"] == 20

    response = client.get("/randoms", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_random_not_found(client, token):
    resp = client.get("/randoms/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
    assert resp.json() == {'detail': 'Random item not found'}


def test_get_random(client, token):
    resp = client.post("/randoms", json={"min_value": 200, "max_value": 300}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    id = resp.json()["id"]
    resp = client.get(f"/randoms/{id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["min_value"] == 200
    assert resp.json()["max_value"] == 300


def test_update_random_not_found(client, token):
    resp = client.patch("/randoms/1", json={"min_value": 2001, "max_value": 3001}, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 404
    assert resp.json() == {'detail': 'Random item not found'}


def test_update_random(client, token):
    resp = client.post("/randoms", json={"min_value": 2000, "max_value": 3000}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    id = resp.json()["id"]
    resp = client.patch(f"/randoms/{id}", json={"min_value": 2001, "max_value": 3001}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["min_value"] == 2001
    assert resp.json()["max_value"] == 3001


def test_delete_random_not_found(client, token):
    resp = client.delete("/randoms/1",headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
    assert resp.json() == {'detail': 'Random item not found'}


def test_delete_random(client, token):
    resp = client.post("/randoms", json={"min_value": 2000, "max_value": 3000}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    id = resp.json()["id"]
    resp = client.delete(f"/randoms/{id}",headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {'ok': True}
