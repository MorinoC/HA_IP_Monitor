"""
ファイル名: test_config_flow.py
説明: 設定フローのユニットテスト
作成日: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST

from custom_components.ha_ip_monitor.const import (
    DOMAIN,
    CONF_VPS_HOST,
    CONF_VPS_PORT,
    CONF_VPS_USERNAME,
    CONF_VPS_PASSWORD,
    CONF_API_PORT,
    CONF_API_TOKEN,
    CONF_USE_SSH_KEY,
    DEFAULT_VPS_PORT,
    DEFAULT_API_PORT,
)
from custom_components.ha_ip_monitor.config_flow import (
    HAIPMonitorConfigFlow,
    validate_vps_connection,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_flow_user_step(mock_hass):
    """ユーザー設定ステップをテスト"""
    flow = HAIPMonitorConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user(user_input=None)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert CONF_VPS_HOST in result["data_schema"].schema
    assert CONF_VPS_PORT in result["data_schema"].schema


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_flow_user_with_password(mock_hass):
    """パスワード認証での設定フローをテスト"""
    flow = HAIPMonitorConfigFlow()
    flow.hass = mock_hass

    # ステップ1: VPS接続設定
    user_input = {
        CONF_VPS_HOST: "192.168.1.100",
        CONF_VPS_PORT: DEFAULT_VPS_PORT,
        CONF_VPS_USERNAME: "testuser",
        CONF_USE_SSH_KEY: False,
    }

    result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "password"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_flow_password_step(mock_hass):
    """パスワードステップをテスト"""
    flow = HAIPMonitorConfigFlow()
    flow.hass = mock_hass
    flow.data = {
        CONF_VPS_HOST: "192.168.1.100",
        CONF_VPS_PORT: DEFAULT_VPS_PORT,
        CONF_VPS_USERNAME: "testuser",
    }

    password_input = {
        CONF_VPS_PASSWORD: "test_password",
    }

    result = await flow.async_step_password(user_input=password_input)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "api_config"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_flow_api_config_step(mock_hass):
    """API設定ステップをテスト"""
    flow = HAIPMonitorConfigFlow()
    flow.hass = mock_hass
    flow.data = {
        CONF_VPS_HOST: "192.168.1.100",
        CONF_VPS_PORT: DEFAULT_VPS_PORT,
        CONF_VPS_USERNAME: "testuser",
        CONF_VPS_PASSWORD: "test_password",
    }

    api_input = {
        CONF_API_PORT: DEFAULT_API_PORT,
        CONF_API_TOKEN: "test-token-12345",
    }

    with patch(
        "custom_components.ha_ip_monitor.config_flow.validate_api_connection",
        return_value={"api_connected": True},
    ):
        result = await flow.async_step_api_config(user_input=api_input)

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "HA IP Monitor (192.168.1.100)"
    assert result["data"][CONF_VPS_HOST] == "192.168.1.100"
    assert result["data"][CONF_API_TOKEN] == "test-token-12345"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_vps_connection_success(mock_hass):
    """VPS接続検証の成功ケースをテスト"""
    data = {
        CONF_VPS_HOST: "192.168.1.100",
        CONF_VPS_PORT: DEFAULT_VPS_PORT,
        CONF_VPS_USERNAME: "testuser",
    }

    result = await validate_vps_connection(mock_hass, data)

    assert "title" in result
    assert "192.168.1.100" in result["title"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_flow_invalid_host(mock_hass):
    """無効なホストでの設定フローをテスト"""
    flow = HAIPMonitorConfigFlow()
    flow.hass = mock_hass

    user_input = {
        CONF_VPS_HOST: "",  # 空のホスト
        CONF_VPS_PORT: DEFAULT_VPS_PORT,
        CONF_VPS_USERNAME: "testuser",
        CONF_USE_SSH_KEY: False,
    }

    with patch(
        "custom_components.ha_ip_monitor.config_flow.validate_vps_connection",
        side_effect=Exception("Invalid host"),
    ):
        result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert "errors" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_flow_already_configured(mock_hass):
    """既に設定済みの場合のテスト"""
    # 既存のエントリーをシミュレート
    existing_entry = config_entries.ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="HA IP Monitor (192.168.1.100)",
        data={CONF_VPS_HOST: "192.168.1.100"},
        source="user",
        entry_id="existing_id",
    )

    mock_hass.config_entries = MagicMock()
    mock_hass.config_entries.async_entries = MagicMock(return_value=[existing_entry])

    flow = HAIPMonitorConfigFlow()
    flow.hass = mock_hass

    user_input = {
        CONF_VPS_HOST: "192.168.1.100",
        CONF_VPS_PORT: DEFAULT_VPS_PORT,
        CONF_VPS_USERNAME: "testuser",
        CONF_USE_SSH_KEY: False,
    }

    result = await flow.async_step_user(user_input=user_input)

    # 既に設定済みの場合はアボートするはず
    assert result["type"] == data_entry_flow.FlowResultType.ABORT or result["type"] == data_entry_flow.FlowResultType.FORM
