import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "demo@example.com",
            "full_name": "Demo User",
            "password": "secure-password",
        },
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login/json",
        json={"email": "demo@example.com", "password": "secure-password"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]

