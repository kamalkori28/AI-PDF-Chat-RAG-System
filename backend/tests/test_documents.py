import pytest


async def auth_headers(client) -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "docs@example.com",
            "full_name": "Docs User",
            "password": "secure-password",
        },
    )
    response = await client.post(
        "/api/v1/auth/login/json",
        json={"email": "docs@example.com", "password": "secure-password"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf(client):
    headers = await auth_headers(client)
    response = await client.post(
        "/api/v1/upload",
        headers=headers,
        files={"files": ("notes.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 415
    assert "not a PDF" in response.json()["detail"]

