import pytest


@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "username": "newuser",
        "password": "secret123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "username": "dupuser", "password": "secret"}
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json={**payload, "username": "other"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/api/v1/auth/register", json={
        "email": "a@example.com", "username": "sameuser", "password": "secret"
    })
    resp = await client.post("/api/v1/auth/register", json={
        "email": "b@example.com", "username": "sameuser", "password": "secret"
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com", "username": "loginuser", "password": "pass123"
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "login@example.com", "password": "pass123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wp@example.com", "username": "wpuser", "password": "correct"
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "wp@example.com", "password": "wrong"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh(client):
    await client.post("/api/v1/auth/register", json={
        "email": "ref@example.com", "username": "refuser", "password": "pass"
    })
    login = await client.post("/api/v1/auth/login", data={
        "username": "ref@example.com", "password": "pass"
    })
    refresh_token = login.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client):
    await client.post("/api/v1/auth/register", json={
        "email": "rf2@example.com", "username": "rf2user", "password": "pass"
    })
    login = await client.post("/api/v1/auth/login", data={
        "username": "rf2@example.com", "password": "pass"
    })
    access_token = login.json()["access_token"]

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401
