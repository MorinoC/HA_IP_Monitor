"""
ファイル名: test_coordinator.py
説明: データコーディネーターのユニットテスト
作成日: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.ha_ip_monitor.coordinator import HAIPMonitorDataUpdateCoordinator
from custom_components.ha_ip_monitor.const import UPDATE_INTERVAL


@pytest.mark.unit
@pytest.mark.asyncio
async def test_coordinator_initialization(mock_hass, mock_config_entry):
    """コーディネーターの初期化をテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    assert coordinator.hass == mock_hass
    assert coordinator.entry == mock_config_entry
    assert coordinator.vps_host == "192.168.1.100"
    assert coordinator.api_port == 5001
    assert coordinator.api_token == "test-token-12345"
    assert coordinator.api_base_url == "http://192.168.1.100:5001"
    assert coordinator.update_interval == timedelta(seconds=UPDATE_INTERVAL)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_vps_status_success(
    mock_hass, mock_config_entry, mock_api_response_status
):
    """VPSステータス取得の成功ケースをテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    with patch.object(
        coordinator, "_make_api_request", return_value=mock_api_response_status
    ):
        status = await coordinator._fetch_vps_status()

        assert status["blocked_ips_today"] == 15
        assert status["ssh_attacks_today"] == 234
        assert status["vpn_attacks_today"] == 45
        assert status["system_status"] == "online"
        assert status["cpu_usage"] == 25.5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_threats_success(
    mock_hass, mock_config_entry, mock_api_response_threats
):
    """脅威データ取得の成功ケースをテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    with patch.object(
        coordinator, "_make_api_request", return_value=mock_api_response_threats
    ):
        threats = await coordinator._fetch_threats()

        assert threats["threat_level"] == "high"
        assert threats["total_threats"] == 42
        assert len(threats["threat_list"]) == 2
        assert threats["threat_list"][0]["ip_address"] == "185.200.116.43"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_update_data_success(
    mock_hass, mock_config_entry, mock_api_response_status, mock_api_response_threats
):
    """データ更新の成功ケースをテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    with patch.object(
        coordinator, "_fetch_vps_status", return_value=mock_api_response_status
    ), patch.object(
        coordinator, "_fetch_threats", return_value=mock_api_response_threats
    ):
        data = await coordinator._async_update_data()

        assert "status" in data
        assert "threats" in data
        assert "last_update" in data
        assert data["status"]["blocked_ips_today"] == 15
        assert data["threats"]["threat_level"] == "high"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_make_api_request_auth_error(mock_hass, mock_config_entry):
    """API認証エラーのテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    # 401エラーをシミュレート
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.text = AsyncMock(return_value="Unauthorized")

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session.get = AsyncMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_response),
                __aexit__=AsyncMock(),
            )
        )
        mock_session_class.return_value = mock_session

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._make_api_request("http://test.com/api/status")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_make_api_request_http_error(mock_hass, mock_config_entry):
    """HTTP API エラーのテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    # 500エラーをシミュレート
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session.get = AsyncMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_response),
                __aexit__=AsyncMock(),
            )
        )
        mock_session_class.return_value = mock_session

        with pytest.raises(UpdateFailed):
            await coordinator._make_api_request("http://test.com/api/status")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_block_ip_success(mock_hass, mock_config_entry):
    """IPブロック成功のテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    mock_response = {"success": True, "message": "IP blocked successfully"}

    with patch.object(
        coordinator, "_make_api_request", return_value=mock_response
    ), patch.object(coordinator, "async_request_refresh", new_callable=AsyncMock):
        result = await coordinator.async_block_ip("192.168.1.1")

        assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_block_ip_failure(mock_hass, mock_config_entry):
    """IPブロック失敗のテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    mock_response = {"success": False, "error": "Invalid IP address"}

    with patch.object(
        coordinator, "_make_api_request", return_value=mock_response
    ):
        result = await coordinator.async_block_ip("invalid-ip")

        assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unblock_ip_success(mock_hass, mock_config_entry):
    """IPブロック解除成功のテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    mock_response = {"success": True, "message": "IP unblocked successfully"}

    with patch.object(
        coordinator, "_make_api_request", return_value=mock_response
    ), patch.object(coordinator, "async_request_refresh", new_callable=AsyncMock):
        result = await coordinator.async_unblock_ip("192.168.1.1")

        assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_response_success(mock_hass, mock_config_entry):
    """正常なレスポンス処理のテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})

    result = await coordinator._handle_response(mock_response)

    assert result == {"data": "test"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_response_403_forbidden(mock_hass, mock_config_entry):
    """403 Forbiddenレスポンスのテスト"""
    coordinator = HAIPMonitorDataUpdateCoordinator(mock_hass, mock_config_entry)

    mock_response = AsyncMock()
    mock_response.status = 403
    mock_response.text = AsyncMock(return_value="Forbidden")

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._handle_response(mock_response)
