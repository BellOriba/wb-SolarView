import pytest
from fastapi import status
from tests.test_utils import assert_response_status, assert_error_response

SAMPLE_PANEL = {
    "name": "Test Panel",
    "capacity": 0.3,  # kWp
    "efficiency": 18.5,
    "manufacturer": "Test Manufacturer",
    "type": "Monocristalino",
}


@pytest.mark.asyncio
async def test_create_panel_as_admin(client, admin_auth_header):
    response = await client.post(
        "/api/panel-models/", headers=admin_auth_header, json=SAMPLE_PANEL
    )
    assert_response_status(response, status.HTTP_201_CREATED)
    data = response.json()
    assert data["name"] == SAMPLE_PANEL["name"]
    assert data["manufacturer"] == SAMPLE_PANEL["manufacturer"]
    assert data["capacity"] == SAMPLE_PANEL["capacity"]
    assert data["efficiency"] == SAMPLE_PANEL["efficiency"]
    assert data["type"] == SAMPLE_PANEL["type"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_panel_as_regular_user(client, user_auth_header):
    response = await client.post(
        "/api/panel-models/", headers=user_auth_header, json=SAMPLE_PANEL
    )
    assert_error_response(response, status.HTTP_403_FORBIDDEN)


@pytest.mark.asyncio
async def test_get_panels(client, admin_auth_header):
    await client.post(
        "/api/panel-models/", headers=admin_auth_header, json=SAMPLE_PANEL
    )

    response = await client.get("/api/panel-models/", headers=admin_auth_header)
    assert_response_status(response, status.HTTP_200_OK)
    panels = response.json()
    assert isinstance(panels, list)
    assert len(panels) > 0
    assert "name" in panels[0]
    assert "manufacturer" in panels[0]
    assert "capacity" in panels[0]


@pytest.mark.asyncio
async def test_get_panel_by_id(client, admin_auth_header):
    create_response = await client.post(
        "/api/panel-models/", headers=admin_auth_header, json=SAMPLE_PANEL
    )
    panel_id = create_response.json()["id"]

    response = await client.get(
        f"/api/panel-models/{panel_id}", headers=admin_auth_header
    )
    assert_response_status(response, status.HTTP_200_OK)
    panel = response.json()
    assert panel["id"] == panel_id
    assert panel["name"] == SAMPLE_PANEL["name"]


@pytest.mark.asyncio
async def test_get_nonexistent_panel(client, admin_auth_header):
    response = await client.get(
        "/api/panel-models/550e8400-e29b-41d4-a716-446655440000",
        headers=admin_auth_header,
    )
    assert_error_response(response, status.HTTP_404_NOT_FOUND)


@pytest.mark.asyncio
async def test_update_panel_as_admin(client, admin_auth_header):
    create_response = await client.post(
        "/api/panel-models/", headers=admin_auth_header, json=SAMPLE_PANEL
    )
    panel_id = create_response.json()["id"]

    update_data = {"name": "Updated Panel Name", "efficiency": 19.0}
    response = await client.put(
        f"/api/panel-models/{panel_id}", headers=admin_auth_header, json=update_data
    )
    assert_response_status(response, status.HTTP_200_OK)

    panel = response.json()
    assert panel["name"] == update_data["name"]
    assert panel["efficiency"] == update_data["efficiency"]
    assert panel["manufacturer"] == SAMPLE_PANEL["manufacturer"]


@pytest.mark.asyncio
async def test_update_panel_as_regular_user(
    client, admin_auth_header, user_auth_header
):
    create_response = await client.post(
        "/api/panel-models/", headers=admin_auth_header, json=SAMPLE_PANEL
    )
    panel_id = create_response.json()["id"]

    response = await client.put(
        f"/api/panel-models/{panel_id}",
        headers=user_auth_header,
        json={"name": "Hacked Panel"},
    )
    assert_error_response(response, status.HTTP_403_FORBIDDEN)


@pytest.mark.asyncio
async def test_delete_panel_as_admin(client, admin_auth_header):
    create_response = await client.post(
        "/api/panel-models/", headers=admin_auth_header, json=SAMPLE_PANEL
    )
    panel_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/panel-models/{panel_id}", headers=admin_auth_header
    )
    assert_response_status(response, status.HTTP_204_NO_CONTENT)

    response = await client.get(
        f"/api/panel-models/{panel_id}", headers=admin_auth_header
    )
    assert_error_response(response, status.HTTP_404_NOT_FOUND)


@pytest.mark.asyncio
async def test_delete_panel_as_regular_user(
    client, admin_auth_header, user_auth_header
):
    create_response = await client.post(
        "/api/panel-models/", headers=admin_auth_header, json=SAMPLE_PANEL
    )
    panel_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/panel-models/{panel_id}", headers=user_auth_header
    )
    assert_error_response(response, status.HTTP_403_FORBIDDEN)


@pytest.mark.asyncio
async def test_delete_nonexistent_panel(client, admin_auth_header):
    response = await client.delete(
        "/api/panel-models/550e8400-e29b-41d4-a716-446655440000",
        headers=admin_auth_header,
    )
    assert_error_response(response, status.HTTP_404_NOT_FOUND)


@pytest.mark.asyncio
async def test_search_panels(client, admin_auth_header):
    panels = [
        {
            "name": "Panel A",
            "capacity": 0.3,
            "efficiency": 18.5,
            "manufacturer": "SolarTech",
            "type": "Monocristalino",
        },
        {
            "name": "Panel B",
            "capacity": 0.35,
            "efficiency": 19.0,
            "manufacturer": "EcoPower",
            "type": "Monocristalino",
        },
        {
            "name": "Panel C",
            "capacity": 0.4,
            "efficiency": 20.0,
            "manufacturer": "SolarTech",
            "type": "Monocristalino",
        },
    ]

    for panel in panels:
        await client.post("/api/panel-models/", headers=admin_auth_header, json=panel)

    response = await client.get(
        "/api/panel-models/?manufacturer=SolarTech", headers=admin_auth_header
    )
    assert_response_status(response, status.HTTP_200_OK)
    results = response.json()
    assert len(results) >= 2
    assert all(panel["manufacturer"] == "SolarTech" for panel in results)

    response = await client.get(
        "/api/panel-models/?min_power=0.35", headers=admin_auth_header
    )
    assert_response_status(response, status.HTTP_200_OK)
    results = response.json()
    assert len(results) >= 2
    assert all(panel["capacity"] >= 0.35 for panel in results)

    response = await client.get(
        "/api/panel-models/?max_price=1500", headers=admin_auth_header
    )
    assert_response_status(response, status.HTTP_200_OK)
    results = response.json()
    assert len(results) >= 0
    assert all(panel.get("price_brl", 0) <= 1500 for panel in results)

    response = await client.get(
        "/api/panel-models/?manufacturer=SolarTech&min_efficiency=19.5",
        headers=admin_auth_header,
    )
    assert_response_status(response, status.HTTP_200_OK)
    results = response.json()
    assert len(results) >= 1
    assert all(
        r["manufacturer"] == "SolarTech" and r["efficiency"] >= 19.5 for r in results
    )
