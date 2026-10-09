"""
Integration tests for User Authentication, Multi-Tenant Project Isolation,
Scene Versioning Graph (v1 -> v2), and Agent Telemetry.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_user_registration_and_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register User
        reg_payload = {
            "email": "architect@sceneforge.ai",
            "password": "secure_password_123",
            "full_name": "Chief 3D Architect"
        }
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 200
        token_data = res.json()
        assert "access_token" in token_data
        assert token_data["email"] == "architect@sceneforge.ai"
        token = token_data["access_token"]

        # 2. Duplicate registration fails
        res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_dup.status_code == 400

        # 3. Login with valid credentials
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "architect@sceneforge.ai",
            "password": "secure_password_123"
        })
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

        # 4. Login with invalid password fails
        bad_login = await client.post("/api/v1/auth/login", json={
            "email": "architect@sceneforge.ai",
            "password": "wrong_password"
        })
        assert bad_login.status_code == 401

        # 5. Access profile with token
        headers = {"Authorization": f"Bearer {token}"}
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "architect@sceneforge.ai"


@pytest.mark.asyncio
async def test_project_lifecycle_and_tenant_isolation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User A Setup
        res_a = await client.post("/api/v1/auth/register", json={
            "email": "user_a@test.com",
            "password": "password_a"
        })
        token_a = res_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # User B Setup
        res_b = await client.post("/api/v1/auth/register", json={
            "email": "user_b@test.com",
            "password": "password_b"
        })
        token_b = res_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A creates Project
        create_res = await client.post("/api/v1/projects", headers=headers_a, json={
            "name": "Superyacht Odyssey",
            "category": "boat",
            "description": "Luxury expedition yacht"
        })
        assert create_res.status_code == 200
        project_a_id = create_res.json()["id"]

        # User B lists projects -> should see 0
        list_b = await client.get("/api/v1/projects", headers=headers_b)
        assert list_b.status_code == 200
        assert len(list_b.json()) == 0

        # User B cannot access User A's project
        get_b = await client.get(f"/api/v1/projects/{project_a_id}", headers=headers_b)
        assert get_b.status_code == 404


@pytest.mark.asyncio
async def test_project_scene_versioning_and_telemetry():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user
        reg = await client.post("/api/v1/auth/register", json={
            "email": "creator@sceneforge.ai",
            "password": "password123"
        })
        headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

        # Create project
        proj = await client.post("/api/v1/projects", headers=headers, json={
            "name": "Expedition Cruiser",
            "category": "boat"
        })
        proj_id = proj.json()["id"]

        # 1. Generate Scene v1
        gen_res = await client.post(
            f"/api/v1/projects/{proj_id}/generate",
            headers=headers,
            json={"prompt": "Create a luxury yacht with teak decking."}
        )
        assert gen_res.status_code == 200
        v1_data = gen_res.json()
        assert v1_data["version_number"] == 1
        assert "scene_id" in v1_data

        # 2. Modify Scene -> creates Scene v2
        edit_res = await client.post(
            f"/api/v1/projects/{proj_id}/edit",
            headers=headers,
            json={"instruction": "Make it 20% longer and add a swimming platform."}
        )
        assert edit_res.status_code == 200
        v2_data = edit_res.json()
        assert v2_data["version_number"] == 2

        # 3. Query all historical scene versions
        scenes_res = await client.get(f"/api/v1/projects/{proj_id}/scenes", headers=headers)
        assert scenes_res.status_code == 200
        scenes_list = scenes_res.json()
        assert len(scenes_list) == 2
        assert scenes_list[0]["version_number"] == 1
        assert scenes_list[1]["version_number"] == 2

        # 4. Query Agent Telemetry Runs
        runs_res = await client.get(f"/api/v1/projects/{proj_id}/runs", headers=headers)
        assert runs_res.status_code == 200
        runs_list = runs_res.json()
        assert len(runs_list) >= 2
        assert len(runs_list[0]["actions"]) >= 1
