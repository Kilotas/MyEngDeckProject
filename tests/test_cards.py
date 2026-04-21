import pytest


@pytest.fixture
async def deck_id(auth_client):
    resp = await auth_client.post("/api/v1/decks", json={"name": "CardDeck", "level": "beginner"})
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_card(auth_client, deck_id):
    resp = await auth_client.post(f"/api/v1/decks/{deck_id}/cards", json={
        "word": "apple", "translation": "яблоко"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["word"] == "apple"
    assert data["translation"] == "яблоко"
    assert data["deck_id"] == deck_id


@pytest.mark.asyncio
async def test_list_cards(auth_client, deck_id):
    await auth_client.post(f"/api/v1/decks/{deck_id}/cards", json={"word": "cat", "translation": "кот"})
    await auth_client.post(f"/api/v1/decks/{deck_id}/cards", json={"word": "dog", "translation": "пёс"})
    resp = await auth_client.get(f"/api/v1/decks/{deck_id}/cards")
    assert resp.status_code == 200
    words = [c["word"] for c in resp.json()]
    assert "cat" in words
    assert "dog" in words


@pytest.mark.asyncio
async def test_update_card(auth_client, deck_id):
    card = (await auth_client.post(f"/api/v1/decks/{deck_id}/cards", json={
        "word": "old", "translation": "старый"
    })).json()
    resp = await auth_client.patch(f"/api/v1/decks/{deck_id}/cards/{card['id']}", json={
        "translation": "обновлённый"
    })
    assert resp.status_code == 200
    assert resp.json()["translation"] == "обновлённый"
    assert resp.json()["word"] == "old"


@pytest.mark.asyncio
async def test_delete_card(auth_client, deck_id):
    card = (await auth_client.post(f"/api/v1/decks/{deck_id}/cards", json={
        "word": "bye", "translation": "пока"
    })).json()
    resp = await auth_client.delete(f"/api/v1/decks/{deck_id}/cards/{card['id']}")
    assert resp.status_code == 204
    cards = (await auth_client.get(f"/api/v1/decks/{deck_id}/cards")).json()
    assert all(c["id"] != card["id"] for c in cards)


@pytest.mark.asyncio
async def test_create_card_wrong_deck(auth_client):
    resp = await auth_client.post(
        "/api/v1/decks/00000000-0000-0000-0000-000000000000/cards",
        json={"word": "x", "translation": "y"}
    )
    assert resp.status_code == 404
