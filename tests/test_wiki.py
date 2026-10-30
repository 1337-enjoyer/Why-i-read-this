from fastapi import status


REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/jwt/login"
RANDOM_URL = "/wiki/random"
RANDOM_AUTH_URL = "/wiki/random/auth"
HISTORY_URL = "/wiki/history"
ARTICLE_URL = "/wiki/article/6984570"

TEST_EMAIL = "wiki@example.com"
TEST_PASSWORD = "secret123"
TEST_TITLE = "Натюрморт с драпировкой"
TEST_PAGE_ID = 6984570


async def _get_token(client) -> str:
    await client.post(
        REGISTER_URL,
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    login = await client.post(
        LOGIN_URL,
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    return login.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_random_article_guest(client, mock_wiki_ok):
    response = await client.get(RANDOM_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == TEST_TITLE
    assert data["page_id"] == TEST_PAGE_ID
    assert data["extract"]
    assert data["image_url"] == "https://example.com/img.jpg"


async def test_random_article_returns_502_when_wiki_empty(
    client, mock_wiki_empty
):
    response = await client.get(RANDOM_URL)

    assert response.status_code == status.HTTP_502_BAD_GATEWAY


async def test_random_auth_saves_to_history(client, mock_wiki_ok):
    token = await _get_token(client)

    response = await client.get(
        RANDOM_AUTH_URL, headers=_auth_header(token)
    )
    assert response.status_code == status.HTTP_200_OK

    history = await client.get(
        HISTORY_URL, headers=_auth_header(token)
    )
    assert history.status_code == status.HTTP_200_OK
    items = history.json()
    assert len(items) == 1
    assert items[0]["title"] == TEST_TITLE
    assert items[0]["page_id"] == TEST_PAGE_ID


async def test_random_auth_requires_token(client):
    response = await client.get(RANDOM_AUTH_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_history_requires_auth(client):
    response = await client.get(HISTORY_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_history_empty_for_new_user(client):
    token = await _get_token(client)
    response = await client.get(
        HISTORY_URL, headers=_auth_header(token)
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


async def test_clear_history(client, mock_wiki_ok):
    token = await _get_token(client)
    headers = _auth_header(token)

    await client.get(RANDOM_AUTH_URL, headers=headers)
    await client.get(RANDOM_AUTH_URL, headers=headers)

    history_before = await client.get(HISTORY_URL, headers=headers)
    assert len(history_before.json()) == 2

    clear = await client.delete(HISTORY_URL, headers=headers)
    assert clear.status_code == status.HTTP_204_NO_CONTENT

    history_after = await client.get(HISTORY_URL, headers=headers)
    assert history_after.json() == []


async def test_clear_history_requires_auth(client):
    response = await client.delete(HISTORY_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_article_by_id(client, mock_wiki_ok):
    response = await client.get(ARTICLE_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page_id"] == TEST_PAGE_ID
    assert data["title"] == TEST_TITLE
    assert data["extract"]
