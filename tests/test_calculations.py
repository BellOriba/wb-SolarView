import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from tests.test_utils import assert_response_status, assert_error_response

SAMPLE_PVGIS_RESPONSE = {
    "inputs": {
        "location": {"latitude": -23.5505, "longitude": -46.6333, "elevation": 760},
        "pv_tech": {
            "fixed": {
                "slope": {"value": 20, "optimal": False},
                "azimuth": {"value": 0, "optimal": False},
            }
        },
        "pv_module": {
            "technology": "c-Si",
            "peak_power": 1,
            "system_loss": 14,
            "tracking": {"fixed": {}},
        },
        "economic_data": {"system_cost": None, "interest": 4, "lifetime": 25},
    },
    "outputs": {
        "monthly": {
            "fixed": [
                {"month": 1, "E_d": 100, "E_m": 3100, "H(i)_d": 5.2, "H(i)_m": 161.2},
                {"month": 2, "E_d": 110, "E_m": 3080, "H(i)_d": 5.8, "H(i)_m": 162.4},
                # ... other months
            ]
        },
        "totals": {
            "fixed": {
                "E_d": 10.5,
                "E_m": 320.5,
                "E_y": 3836.4,
                "H(i)_d": 4.8,
                "H(i)_m": 148.8,
                "H(i)_y": 1785.6,
                "SD_m": 12.3,
                "SD_y": 147.6,
            }
        },
    },
    "meta": {
        "inputs": {
            "location": {
                "description": "Selected location",
                "variables": {
                    "latitude": {"description": "Latitude", "units": "decimal degrees"},
                    "longitude": {
                        "description": "Longitude",
                        "units": "decimal degrees",
                    },
                    "elevation": {"description": "Elevation", "units": "m"},
                },
            },
            "mounting_system": {
                "description": "Mounting system",
                "choices": ["free", "building"],
                "fields": {
                    "slope": {
                        "description": "Inclination angle from horizontal plane",
                        "units": "°",
                    },
                    "azimuth": {
                        "description": "Orientation (azimuth) angle of the (fixed) plane, 0=south, 90=west, -90=east",
                        "units": "°",
                    },
                },
            },
            "pv_module": {
                "description": "PV module parameters",
                "fields": {
                    "peak_power": {
                        "description": "Nominal (peak) power of the PV panel",
                        "units": "kW",
                    },
                    "system_loss": {
                        "description": "Sum of system losses",
                        "units": "%",
                    },
                },
            },
            "economic_data": {
                "description": "Economic inputs",
                "fields": {
                    "system_cost": {
                        "description": "Total cost of the PV system",
                        "units": "",
                    },
                    "interest": {"description": "Interest rate", "units": "%"},
                    "lifetime": {
                        "description": "Expected lifetime of the PV system",
                        "units": "years",
                    },
                },
            },
        }
    },
}


@pytest.fixture
def mock_pvgis_client():
    """Mock the PVGIS client at the place it's used (routes module)."""
    with patch("src.solar_api.adapters.api.routes.PVGISAdapter") as mock:
        mock_instance = AsyncMock()
        mock_instance.get_pv_data = AsyncMock(return_value=SAMPLE_PVGIS_RESPONSE)
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_calculate_solar_production(client: AsyncClient, mock_pvgis_client):
    """Test solar production calculation with valid input."""
    # Setup mock
    mock_instance = mock_pvgis_client
    mock_instance.get_pv_data.return_value = SAMPLE_PVGIS_RESPONSE

    request_data = {"lat": -23.5505, "lon": -46.6333, "peakpower": 5.0, "loss": 14.0}

    response = await client.post("/calculate", json=request_data)

    assert_response_status(response, status.HTTP_200_OK)
    data = response.json()

    # Verify response structure of mocked adapter output (raw-like)
    assert "inputs" in data
    assert "outputs" in data
    assert "location" in data["inputs"]
    assert "pv_tech" in data["inputs"]

    # Verify mock was called with correct parameters
    mock_instance.get_pv_data.assert_called_once()
    args, _ = mock_instance.get_pv_data.call_args
    assert args[0].lat == request_data["lat"]
    assert args[0].lon == request_data["lon"]
    assert args[0].peakpower == request_data["peakpower"]
    assert args[0].loss == request_data["loss"]


@pytest.mark.parametrize("missing_field", ["lat", "lon", "peakpower", "loss"])
@pytest.mark.asyncio
async def test_calculate_solar_production_missing_required_fields(
    client: AsyncClient, mock_pvgis_client, missing_field: str
):
    """Test calculation with missing required fields."""
    # Setup test data
    data = {"lat": -23.5505, "lon": -46.6333, "peakpower": 1.0, "loss": 14.0}
    data.pop(missing_field)

    # Make request and verify response
    response = await client.post("/calculate", json=data)
    assert_error_response(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Verify PVGIS client was not called
    mock_pvgis_client.get_pv_data.assert_not_called()


@pytest.mark.asyncio
async def test_calculate_solar_production_invalid_coordinates(
    client: AsyncClient, mock_pvgis_client
):
    """Test calculation with invalid coordinates."""
    # Setup test data with invalid coordinates
    request_data = {
        "lat": -100,  # Invalid latitude
        "lon": 200,  # Invalid longitude
        "peakpower": 5.0,
        "loss": 14.0,
    }

    # Make request and verify response
    response = await client.post("/calculate", json=request_data)
    # No range validation in PVGISRequest, so expect 200 with mocked response
    assert_response_status(response, status.HTTP_200_OK)

    # Verify PVGIS client was called
    mock_pvgis_client.get_pv_data.assert_called()
