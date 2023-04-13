"""Tests for the app module.
"""
from fastapi.testclient import TestClient

from app import app

def test_index_route() -> None:
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == 200
    assert response.json()['message'] == "Hello World"
    assert len(response.json()) == 1


def test_echo_endpoint() -> None:
    client = TestClient(app)
    response = client.get('/echo/Hello')

    assert response.status_code == 200
    assert response.json()['message1'] == "Hello"
    assert len(response.json()) == 1
