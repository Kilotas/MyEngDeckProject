import pytest


@pytest.fixture
async def card_id(auth_client):
    deck = (await auth_client.post("/api/v1/decks", json={"name": "ReviewDeck", "level": "beginner"})).json()
    card = (await auth_client.post(f"/api/v1/decks/{deck['id']}/cards", json={
        "word": "hello", "translation": "привет"
    })).json()
    return card["id"]


@pytest.mark.asyncio
async def test_submit_review(auth_client, card_id):
    resp = await auth_client.post("/api/v1/reviews", json={"card_id": card_id, "quality": 4})
    assert resp.status_code == 200
    data = resp.json()
    assert data["card_id"] == card_id
    assert data["repetitions"] == 1
    assert data["interval"] == 1


@pytest.mark.asyncio
async def test_submit_review_fail_increments_interval(auth_client, card_id):
    # Сначала успешное повторение
    await auth_client.post("/api/v1/reviews", json={"card_id": card_id, "quality": 5})
    # Потом провал — repetitions и interval должны сброситься
    resp = await auth_client.post("/api/v1/reviews", json={"card_id": card_id, "quality": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["repetitions"] == 0
    assert data["interval"] == 1


@pytest.mark.asyncio
async def test_get_due_cards(auth_client, card_id):
    # Новая карточка сразу попадает в due (next_review_at = now)
    await auth_client.post("/api/v1/reviews", json={"card_id": card_id, "quality": 5})
    # После успешного ответа next_review_at уходит в будущее
    resp = await auth_client.get("/api/v1/reviews/due")
    assert resp.status_code == 200
    # Карточка с interval=1 не должна быть в due прямо сейчас
    ids = [r["card_id"] for r in resp.json()]
    assert card_id not in ids


@pytest.mark.asyncio
async def test_invalid_quality(auth_client, card_id):
    resp = await auth_client.post("/api/v1/reviews", json={"card_id": card_id, "quality": 6})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_review_card_not_found(auth_client):
    resp = await auth_client.post("/api/v1/reviews", json={
        "card_id": "00000000-0000-0000-0000-000000000000", "quality": 3
    })
    assert resp.status_code == 404
