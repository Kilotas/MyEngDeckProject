import pytest


@pytest.mark.asyncio
async def test_create_deck(auth_client):
    resp = await auth_client.post("/api/v1/decks", json={
        "name": "My Deck", "level": "beginner"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Deck"
    assert data["level"] == "beginner"


@pytest.mark.asyncio
async def test_list_decks(auth_client):
    await auth_client.post("/api/v1/decks", json={"name": "D1", "level": "beginner"})
    await auth_client.post("/api/v1/decks", json={"name": "D2", "level": "advanced"})
    resp = await auth_client.get("/api/v1/decks")
    assert resp.status_code == 200
    names = [d["name"] for d in resp.json()]
    assert "D1" in names
    assert "D2" in names


@pytest.mark.asyncio
async def test_get_deck(auth_client):
    created = (await auth_client.post("/api/v1/decks", json={
        "name": "GetMe", "level": "intermediate"
    })).json()
    resp = await auth_client.get(f"/api/v1/decks/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_get_deck_not_found(auth_client):
    resp = await auth_client.get("/api/v1/decks/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_deck(auth_client):
    created = (await auth_client.post("/api/v1/decks", json={
        "name": "Old Name", "level": "beginner"
    })).json()
    resp = await auth_client.patch(f"/api/v1/decks/{created['id']}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"
    assert resp.json()["level"] == "beginner"


@pytest.mark.asyncio
async def test_delete_deck(auth_client):
    created = (await auth_client.post("/api/v1/decks", json={
        "name": "ToDelete", "level": "beginner"
    })).json()
    resp = await auth_client.delete(f"/api/v1/decks/{created['id']}")
    assert resp.status_code == 204
    assert (await auth_client.get(f"/api/v1/decks/{created['id']}")).status_code == 404


@pytest.mark.asyncio
async def test_deck_requires_auth(client):
    resp = await client.get("/api/v1/decks")
    assert resp.status_code == 401
