from fastapi import status


REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/jwt/login"
ME_URL = "/users/me"

TEST_EMAIL = "flow@example.com"
TEST_PASSWORD = "secret123"


async def test_register_and_login_flow(client):
    reg = await client.post(
        REGISTER_URL,
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert reg.status_code == status.HTTP_201_CREATED

    login = await client.post(
        LOGIN_URL,
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert login.status_code == status.HTTP_200_OK
    token = login.json()["access_token"]

    me = await client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["email"] == TEST_EMAIL


async def test_me_requires_token(client):
    response = await client.get(ME_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
